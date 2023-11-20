package com.elysum.springboot.service;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.elysum.springboot.exception.DaoException;
import com.elysum.springboot.dao.SnowflakeQueryDao;
import com.elysum.springboot.exception.ServiceException;

@Service("snowflakeQueryService")
public class SnowflakeQueryServiceImpl implements SnowflakeQueryService {

	@Autowired
	SnowflakeQueryDao snowflakeQueryDao;
	
	@Override
	public List<Object> executeSampleQuery() throws ServiceException {
		try {
			return snowflakeQueryDao.executeSampleQuery();
		} catch (Exception e) {
			throw new ServiceException(e);
		}
	}
	
	@Override
	public List<List<Object>> executeQueries(List<String> queryList) throws ServiceException{
	    try {
            return snowflakeQueryDao.executeQueries(queryList);
        } catch (Exception e) {
            throw new ServiceException(e);
        }
	}

    @Override
    public String executeAggregationQuery(String whereCondition, String bucketType, String interval,String viewName)
            throws ServiceException {
        try {
            return snowflakeQueryDao.executeAggregationQuery(whereCondition, bucketType, interval, viewName);
        } catch (Exception e) {
            throw new ServiceException(e);
        }
    }
    
    @Override
    public List<String> getColumnMetaData(String viewName) throws DaoException {
    	// TODO Auto-generated method stub
    	return snowflakeQueryDao.getColumnMetaData(viewName);
    }

	@Override
	public String executeStoredProceedure(String sp) throws DaoException {
		// TODO Auto-generated method stub
		return snowflakeQueryDao.executeStoredProceedure(sp);
	}
    
	@Override
	public List<Object> executeQuery(String sqlQuery) throws ServiceException {
		try {
			//snowflakeQueryDao = new SnowflakeQueryDaoImpl();
			return snowflakeQueryDao.executeQuery(sqlQuery);
		} catch (Exception e) {
			throw new ServiceException(e);
		}
	}

}
