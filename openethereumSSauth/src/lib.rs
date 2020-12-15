#![feature(test)]
#![allow(non_snake_case)]
#[macro_use]
extern crate jsonrpc_client_core;
extern crate jsonrpc_client_http;
extern crate rand;
extern crate test;

use primitive_types::H160;
use sha2::{Digest, Sha256};
use std::str::FromStr;
mod api;
mod blockchain;

type Password = str;
type Data = String;

use crate::blockchain::Blockchain;
use crate::blockchain::DocumentKey;
use ethcontract::transaction::TransactionResult;
use failure::Error;
use tokio::runtime::Runtime;

pub struct CryptoSecretStore {
    blockchain: Blockchain,
    address: H160,
    password: String,
    rt: Runtime,
}

impl CryptoSecretStore {
    pub fn new(addr: &str, password: &str) -> Self {
        let address = H160::from_str(addr).unwrap();
        let password = password.to_string();
        let blockchain = Blockchain::new(
            address,
            &password,
            "http://127.0.0.1:8010", //"http://34.91.1.238:8010",
            "http://127.0.0.1:8545", //"http://34.91.1.238:8010",
        )
        .unwrap();

        let rt = Runtime::new().unwrap();

        CryptoSecretStore {
            blockchain,
            address,
            password,
            rt,
        }
    }

    pub fn generate_id(&mut self, document: &str) -> String {
        format!("{:x}", Sha256::digest(&document.as_bytes()))
    }

    pub fn generate_key(&mut self, id: &str, threshold: u32) -> Result<DocumentKey, Error> {
        let document_id = &format!("{:x}", Sha256::digest(&id.as_bytes()));
        self.rt.block_on(self.blockchain.generate_keys(
            self.address,
            &self.password,
            document_id,
            threshold,
        ))
    }

    pub fn encrypt(
        &mut self,
        id: &str,
        document: &str,
        document_key: DocumentKey,
    ) -> Result<String, Error> {
        let document_id = &format!("{:x}", Sha256::digest(&id.as_bytes()));
        self.rt.block_on(self.blockchain.encrypt(
            self.address,
            &self.password,
            document_id,
            document,
            document_key,
        ))
    }

    pub fn decrypt(&mut self, id: &str, encrypted_document: &str) -> Result<String, Error> {
        let document_id = &format!("{:x}", Sha256::digest(&id.as_bytes()));
        self.rt.block_on(self.blockchain.decrypt(
            self.address,
            &self.password,
            document_id,
            &encrypted_document.to_string(),
        ))
    }

    pub fn allow_access(
        &mut self,
        document_id: &str,
        addresses: &[H160],
    ) -> Result<TransactionResult, Error> {
        let document_id = &format!("{:x}", Sha256::digest(&document_id.as_bytes()));
        self.rt.block_on(self.blockchain.allow_access(
            self.address,
            &self.password,
            document_id,
            addresses,
        ))
    }

    pub fn check_permissions(&mut self, address: H160, document_id: &str) -> Result<bool, Error> {
        let document_id = &format!("{:x}", Sha256::digest(&document_id.as_bytes()));
        self.rt
            .block_on(self.blockchain.check_permissions(address, document_id))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use ethcontract::U256;
    use primitive_types::H160;
    use rand::distributions::Alphanumeric;
    use rand::{thread_rng, Rng};
    use std::cell::RefCell;
    use std::convert::TryInto;
    use std::fs::OpenOptions;
    use std::io::Write;
    use std::rc::Rc;
    use std::{thread, time};

    struct Message {
        id: String,
        cleartext: String,
        ciphertext: String,
    }

    #[test]
    fn setup1() {
        let address = "18f2801b4c9bab5c9082448cf9b6f73b86321726";
        let password = "alicepwd";
        Rc::new(RefCell::new(CryptoSecretStore::new(address, password)));
    }

    #[test]
    fn setup_encrypt() {
        let address = "18f2801b4c9bab5c9082448cf9b6f73b86321726";
        let password = "alicepwd";
        let store = Rc::new(RefCell::new(CryptoSecretStore::new(address, password)));
        let document: String = thread_rng().sample_iter(&Alphanumeric).take(30).collect();
        let (id, document_key) = generate_key(store.clone(), &document, 2);
        encrypt(store.clone(), id, document, document_key);
    }

    #[test]
    fn time_encrypt_decrypt() {
        let address = "18f2801b4c9bab5c9082448cf9b6f73b86321726";
        let password = "alicepwd";
        let store = Rc::new(RefCell::new(CryptoSecretStore::new(address, password)));
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .append(true)
            .open("./stats.txt")
            .unwrap();

        let _ = writeln!(file, "[");

        let limit = 25;
        for threshold in 0..limit {
            let now = time::Instant::now();
            for _i in 0..5 {
                let document: String = thread_rng().sample_iter(&Alphanumeric).take(30).collect();
                let (id, document_key) = generate_key(store.clone(), &document, 2);
                let message = encrypt(store.clone(), id, document, document_key);
                {
                    let address = H160::from_str(address).unwrap();
                    let addresses = vec![address];
                    let mut store = store.borrow_mut();
                    let result = store.allow_access(&message.id, &addresses).unwrap();
                    assert_eq!(result.is_receipt(), true);
                }
                decrypt(store.clone(), message);
            }
            let durtation = now.elapsed();
            println!("Threshold: {}, Elapsed time {:?}", threshold, durtation / 5);
            if threshold == limit - 1 {
                let _ = writeln!(file, "{}", (durtation / 5).as_millis());
            } else {
                let _ = writeln!(file, "{},", (durtation / 5).as_millis());
            }
        }
        let _ = writeln!(file, "]");
    }

    #[test]
    fn time_encrypt_decrypt_var_threshold() {
        let address = "18f2801b4c9bab5c9082448cf9b6f73b86321726";
        let password = "alicepwd";
        let store = Rc::new(RefCell::new(CryptoSecretStore::new(address, password)));
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .append(true)
            .open("./stats.txt")
            .unwrap();

        let _ = writeln!(file, "[");
        let limit = 25;
        let step: u32 = 0;
        for threshold in step..limit {
            let mut messages: Vec<Message> = vec![];

            //Encryption
            let mut duration_crea = time::Duration::from_secs(0);
            let mut duration_encr = time::Duration::from_secs(0);
            for _i in 0..10 {
                thread::sleep(time::Duration::from_millis(300));
                // Create message
                let document: String = thread_rng().sample_iter(&Alphanumeric).take(30).collect();
                // Generate key
                let now_crea = time::Instant::now();
                let (id, document_key) = generate_key(store.clone(), &document, threshold);
                duration_crea += now_crea.elapsed();
                // Encrypt document
                let now_encr = time::Instant::now();
                let msg = encrypt(store.clone(), id, document, document_key);
                duration_encr += now_encr.elapsed();
                messages.push(msg);
            }
            let duration_creation = duration_crea / 10;
            let duration_encrypt = duration_encr / 10;

            // Set Access
            thread::sleep(time::Duration::from_secs(1));
            for i in 0..10 {
                thread::sleep(time::Duration::from_millis(300));
                let address = H160::from_str(address).unwrap();
                let addresses = vec![address];
                let mut store = store.borrow_mut();
                let result = store.allow_access(&messages[i].id, &addresses).unwrap();
                assert_eq!(result.is_receipt(), true);
            }

            // Decrypt
            thread::sleep(time::Duration::from_secs(1));
            let mut duration_decr = time::Duration::from_secs(0);
            for _i in 0..10 {
                thread::sleep(time::Duration::from_millis(300));
                let msg = messages.pop().unwrap();
                let now = time::Instant::now();
                decrypt(store.clone(), msg);
                duration_decr += now.elapsed();
            }
            let duration_decrypt = duration_decr / 10;

            // Output
            println!(
                "Threshold: {}, Elapsed time encryption {:?}, decryption {:?}",
                threshold,
                duration_creation + duration_encrypt,
                duration_decrypt
            );
            let _ = writeln!(
                file,
                "{{\"encryption\" : {}, \"decryption\": {}, \"threshold\" : {}, \"key_generation\" : {}}},",
                (duration_encrypt).as_millis(),
                duration_decrypt.as_millis(),
                threshold,
                duration_creation.as_millis()
            );
        }
        let _ = writeln!(file, "]");
        let _ = writeln!(file, "#Range {}..{} with step {}", step, limit, step);
    }

    #[test]
    fn time_encrypt_decrypt_var_message_size() {
        let address = "18f2801b4c9bab5c9082448cf9b6f73b86321726";
        let password = "alicepwd";
        let store = Rc::new(RefCell::new(CryptoSecretStore::new(address, password)));
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .append(true)
            .open("./stats.txt")
            .unwrap();

        let _ = writeln!(file, "[");
        let sizes: [usize; 13] = [
            10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000, 10000000,
        ];

        // Start test
        for size in &sizes {
            let mut messages: Vec<Message> = vec![];

            // Encryption
            let mut duration_crea = time::Duration::from_secs(0);
            let mut duration_encr = time::Duration::from_secs(0);
            for _i in 0..10 {
                thread::sleep(time::Duration::from_millis(300));
                // Create message
                let document: String = thread_rng()
                    .sample_iter(&Alphanumeric)
                    .take(size.clone())
                    .collect();
                // Generate key
                let now_crea = time::Instant::now();
                let (id, document_key) = generate_key(store.clone(), &document, 2);
                duration_crea += now_crea.elapsed();
                // Encrypt document
                let now_encr = time::Instant::now();
                let msg = encrypt(store.clone(), id, document, document_key);
                duration_encr += now_encr.elapsed();
                messages.push(msg);
            }
            let duration_creation = duration_crea / 10;
            let duration_encrypt = duration_encr / 10;

            // Set Access
            thread::sleep(time::Duration::from_secs(1));
            for i in 0..10 {
                thread::sleep(time::Duration::from_millis(300));
                let address = H160::from_str(address).unwrap();
                let addresses = vec![address];
                let mut store = store.borrow_mut();
                let result = store.allow_access(&messages[i].id, &addresses).unwrap();
                assert_eq!(result.is_receipt(), true);
            }

            // Decryption
            thread::sleep(time::Duration::from_secs(1));
            let mut duration_decr = time::Duration::from_secs(0);
            for _i in 0..10 {
                thread::sleep(time::Duration::from_millis(300));
                let msg = messages.pop().unwrap();
                let now = time::Instant::now();
                decrypt(store.clone(), msg);
                duration_decr += now.elapsed();
            }
            let duration_decrypt = duration_decr / 10;

            // Output
            println!(
                "Message Size: {}, Elapsed time encryption {:?}, decryption {:?}",
                size,
                duration_creation + duration_encrypt,
                duration_decrypt
            );
            let _ = writeln!(
                file,
                "{{\"encryption\" : {}, \"decryption\": {}, \"key_generation\" : {}, \"length\": {}}},",
                duration_encrypt.as_millis(),
                duration_decrypt.as_millis(),
                duration_creation.as_millis(),
                size
            );
        }
        let _ = writeln!(file, "]");
        let _ = writeln!(file, "#Message Size tests");
    }

    #[test]
    fn setup_encrypt_decrypt() {
        let address = "18f2801b4c9bab5c9082448cf9b6f73b86321726";
        let password = "alicepwd";
        let store = Rc::new(RefCell::new(CryptoSecretStore::new(address, password)));
        let document: String = thread_rng().sample_iter(&Alphanumeric).take(30).collect();
        let (id, document_key) = generate_key(store.clone(), &document, 1);
        let message = encrypt(store.clone(), id, document, document_key);
        {
            let address = H160::from_str(address).unwrap();
            let addresses = vec![address];
            let mut store = store.borrow_mut();
            let result = store.check_permissions(address, &message.id).unwrap();
            assert_eq!(result, false);
            let result = store.allow_access(&message.id, &addresses).unwrap();
            assert_eq!(result.is_receipt(), true);
            let result = store.check_permissions(address, &message.id).unwrap();
            assert_eq!(result, true);
        }
        decrypt(store, message);
    }

    #[test]
    fn access_controll() {
        let address = "18f2801b4c9bab5c9082448cf9b6f73b86321726";
        let password = "alicepwd";
        let store = Rc::new(RefCell::new(CryptoSecretStore::new(address, password)));
        let mut store = store.borrow_mut();

        let document: String = thread_rng().sample_iter(&Alphanumeric).take(30).collect();
        let id = store.generate_id(&document);
        let test_addr = H160::random();
        let test_addr1 = H160::random();
        let addresses = vec![test_addr, test_addr1];
        let result = store.check_permissions(test_addr, &id).unwrap();
        assert_eq!(result, false);
        let result = store.check_permissions(test_addr1, &id).unwrap();
        assert_eq!(result, false);
        let result = store.allow_access(&id, &addresses).unwrap();
        assert_eq!(result.is_receipt(), true);
        let result = store.check_permissions(test_addr, &id).unwrap();
        assert_eq!(result, true);
        let result = store.check_permissions(test_addr1, &id).unwrap();
        assert_eq!(result, true);
    }

    #[test]
    fn time_access_controll() {
        let address = "310285E10295850256aa3f7E39e79FD46244cB1D";
        let password = "alicepwd";
        let mut store = CryptoSecretStore::new(address, password);
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .append(true)
            .open("./stats.txt")
            .unwrap();

        let _ = writeln!(file, "[");
        let limit = 100;
        let step: u32 = 10;
        for size in (step..limit).step_by(step.try_into().unwrap()) {
            println!("Step: {} / Limit{}", step, limit);
            let test_addresses: Vec<H160> = (0..size).map(|_| H160::random()).collect();
            let test_ids: Vec<String> = (0..5)
                .map(|_| {
                    let document: String =
                        thread_rng().sample_iter(&Alphanumeric).take(30).collect();
                    let id = store.generate_id(&document);
                    id
                })
                .collect();

            println!("Allow");
            let now = time::Instant::now();
            let mut used_gas: U256 = 0.into();
            for i in 0..5 {
                let result = store.allow_access(&test_ids[i], &test_addresses).unwrap();
                assert_eq!(result.is_receipt(), true);
                used_gas += result.as_receipt().unwrap().gas_used.unwrap();
            }
            let durtation_set_access = now.elapsed() / 5;
            let used_gas = used_gas / 5;

            println!("Check");
            let now = time::Instant::now();
            for i in 0..5 {
                for addr in &test_addresses {
                    let result = store.check_permissions(addr.clone(), &test_ids[i]).unwrap();
                    assert_eq!(result, true);
                }
            }
            let durtation_get_access = now.elapsed() / 5;
            println!("Number of addresses: {}, Elapsed time to set permission {:?}, to check permissions{:?}",
                     size,
                     durtation_set_access,
                     durtation_get_access);
            let _ = writeln!(
                file,
                "{{\"set\" : {}, \"get\": {}, \"no_members\": {}, \"used_gas\": {}}},",
                (durtation_get_access).as_millis(),
                durtation_set_access.as_millis(),
                size,
                used_gas
            );
        }
        let _ = writeln!(file, "]");
        let _ = writeln!(
            file,
            "#Permission time Range {}..{} with step {}",
            step, limit, step
        );
    }

    #[test]
    fn time_check_permissions() {
        let address = "310285E10295850256aa3f7E39e79FD46244cB1D";
        let password = "alicepwd";
        let mut store = CryptoSecretStore::new(address, password);
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .append(true)
            .open("./stats.txt")
            .unwrap();

        let _ = writeln!(file, "[");
        let test_addresses: Vec<H160> = (0..1).map(|_| H160::random()).collect();
        let test_ids: Vec<String> = (0..1)
            .map(|_| {
                let document: String = thread_rng().sample_iter(&Alphanumeric).take(30).collect();
                let id = store.generate_id(&document);
                id
            })
            .collect();

        let mut used_gas: U256 = 0.into();
        for i in 0..1 {
            println!(
                "Document: {:?}, Address: {:?}",
                &test_ids[i], &test_addresses
            );
            let result = store.allow_access(&test_ids[i], &test_addresses).unwrap();
            assert_eq!(result.is_receipt(), true);
            used_gas += result.as_receipt().unwrap().gas_used.unwrap();
        }
        let used_gas = used_gas / 1;

        thread::sleep(time::Duration::from_secs(1));

        let mut duration_decr = time::Duration::from_secs(0);
        let mut i = 0;
        for addr in &test_addresses {
            thread::sleep(time::Duration::from_millis(300));
            let now = time::Instant::now();
            let result = match store.check_permissions(addr.clone(), &test_ids[i]) {
                Ok(re) => re,
                Err(error) => panic!("Check error: {:?}", error),
            };
            duration_decr += now.elapsed();
            assert_eq!(result, true);
            i += 1;
        }
        let durtation_get_access = duration_decr / 1;

        println!(
            "Number of addresses: {}, Elapsed time to check permissions{:?}",
            1, durtation_get_access
        );
        let _ = writeln!(
            file,
            "{{\"get\": {}, \"no_members\": {}, \"used_gas\": {}}},",
            durtation_get_access.as_millis(),
            1,
            used_gas
        );
        let _ = writeln!(file, "]");
        let _ = writeln!(file, "#Permission time");
    }

    fn generate_key(
        store: Rc<RefCell<CryptoSecretStore>>,
        document: &str,
        threshold: u32,
    ) -> (String, DocumentKey) {
        let mut store = store.borrow_mut();
        let id = store.generate_id(&document);
        let document_key = store.generate_key(&id, threshold);
        if !document_key.is_ok() {
            println!("Whats now the error {:?}", document_key);
        }
        assert_eq!(document_key.is_ok(), true);
        (id, document_key.unwrap())
    }

    fn encrypt(
        store: Rc<RefCell<CryptoSecretStore>>,
        id: String,
        document: String,
        document_key: DocumentKey,
    ) -> Message {
        let mut store = store.borrow_mut();
        let ciphertext = store.encrypt(&id, &document, document_key);
        if !ciphertext.is_ok() {
            println!("Whats now the error {:?}", ciphertext);
        }
        assert_eq!(ciphertext.is_ok(), true);
        Message {
            id: id,
            ciphertext: ciphertext.unwrap(),
            cleartext: document,
        }
    }

    fn decrypt(store: Rc<RefCell<CryptoSecretStore>>, message: Message) {
        let mut store = store.borrow_mut();
        let cleartext = store.decrypt(&message.id, &message.ciphertext);
        if !cleartext.is_ok() {
            println!("Whats now the error {:?}", cleartext);
        }
        let cleartext = if !cleartext.is_ok() {
            store.decrypt(&message.id, &message.ciphertext)
        } else {
            cleartext
        };
        assert_eq!(cleartext.is_ok(), true);
        assert_eq!(cleartext.unwrap(), message.cleartext);
    }
}
