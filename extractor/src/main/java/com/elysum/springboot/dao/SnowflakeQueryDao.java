package com.elysum.springboot.dao;

import java.util.List;
import java.util.Map;

import com.elysum.springboot.exception.DaoException;

public interface SnowflakeQueryDao {
	public List<Object> executeSampleQuery() throws DaoException;
	public List<List<Object>> executeQueries(List<String> queryList) throws DaoException;
	public String executeAggregationQuery(String whereCondition, String bucketType, String interval,String viewName) throws DaoException;
	public List<String> getColumnMetaData(String viewName) throws DaoException;
	public String executeStoredProceedure(String sp) throws DaoException;
	public List<Object> executeQuery(String sqlQuery) throws DaoException;
}
