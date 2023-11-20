package com.elysum.springboot.service;

import java.util.List;
import java.util.Map;

import com.elysum.springboot.exception.DaoException;
import com.elysum.springboot.exception.ServiceException;

public interface SnowflakeQueryService {
	public List<Object> executeSampleQuery() throws ServiceException;
	public List<List<Object>> executeQueries(List<String> queryList) throws ServiceException;
	public String executeAggregationQuery(String whereCondition, String bucketType, String interval, String viewName) throws ServiceException;
	public List<String> getColumnMetaData(String viewName) throws DaoException;
	public String executeStoredProceedure(String storedproceedure) throws DaoException;
	public List<Object> executeQuery(String sqlQuery) throws ServiceException;
	
}
