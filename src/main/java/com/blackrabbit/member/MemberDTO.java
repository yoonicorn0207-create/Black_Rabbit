package com.blackrabbit.member;

import com.blackrabbit.kis.KISTokenResDTO;

import java.math.BigInteger;

public class MemberDTO {
	private String username;
	private String password;
	private String email;
	private BigInteger balance;
	// kis
	private String mockAccount;
	private String appKey;
	private String appSecret;
	private Boolean isDeleKis;

	public MemberDTO() {}
	public MemberDTO(String username, String email, BigInteger balance) {
		this.username = username;
		this.email = email;
		this.balance = balance;
	}

	public Boolean getDeleKis() {
		return isDeleKis;
	}

	public void setDeleKis(Boolean deleKis) {
		isDeleKis = deleKis;
	}

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public BigInteger getBalance() {
		return balance;
	}

	public void setBalance(BigInteger balance) {
		this.balance = balance;
	}

	public String getMockAccount() {
		return mockAccount;
	}

	public void setMockAccount(String mockAccount) {
		this.mockAccount = mockAccount;
	}

	public String getAppKey() {
		return appKey;
	}

	public void setAppKey(String appKey) {
		this.appKey = appKey;
	}

	public String getAppSecret() {
		return appSecret;
	}

	public void setAppSecret(String appSecret) {
		this.appSecret = appSecret;
	}
}
