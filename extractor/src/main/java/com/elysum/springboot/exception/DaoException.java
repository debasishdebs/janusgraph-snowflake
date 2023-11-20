package com.elysum.springboot.exception;

public class DaoException extends Exception {

	/**
	 * 
	 */
	private static final long serialVersionUID = -1933874950323499560L;

	public DaoException() {
		super();
	}
	
	public DaoException(String message) {
		super(message);
	}
	
	public DaoException(Exception e) {
		super(e);
	}
	
	public DaoException(String message, Exception e) {
		super(message, e);
	}
}
