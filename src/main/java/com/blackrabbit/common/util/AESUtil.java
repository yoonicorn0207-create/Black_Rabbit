package com.blackrabbit.common.util;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;

@Component
public class AESUtil {
  // KIS key AES256 암호화 진행
  @Value("${aes.secret.key}")
  private String secretKeyString;

  private static SecretKeySpec secretKeySpec;
  private static final String ALGORITHM = "AES";

  // 빈이 생성될 때 키를 초기화
  @PostConstruct
  public void init() {
    secretKeySpec = new SecretKeySpec(secretKeyString.getBytes(), ALGORITHM);
  }

  public String encrypt(String plainText) throws Exception {
    Cipher cipher = Cipher.getInstance(ALGORITHM);
    cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec);
    return Base64.getEncoder().encodeToString(cipher.doFinal(plainText.getBytes()));
  }

  public String decrypt(String encryptedText) throws Exception {
    Cipher cipher = Cipher.getInstance(ALGORITHM);
    cipher.init(Cipher.DECRYPT_MODE, secretKeySpec);
    return new String(cipher.doFinal(Base64.getDecoder().decode(encryptedText)));
  }
}
