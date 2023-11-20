package com.elysum.springboot.dao;

import java.sql.CallableStatement;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.sql.DataSource;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationContext;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import com.sstech.graphdb.extractor.server.SnowflakeConfig;
import com.elysum.springboot.exception.DaoException;

@Component
public class SnowflakeQueryDaoImpl implements SnowflakeQueryDao {

	private final Logger logger = LoggerFactory.getLogger(getClass());
	@Autowired
    JdbcTemplate jdbcTemplate;
	
	@Autowired
	ApplicationContext applicationContext;
	
	private DataSource snowflakeDataSource = null;
	
	private DataSource getSnowFlakeDataSource() {
		if (this.snowflakeDataSource == null) {
			if (logger.isDebugEnabled()) {
				logger.debug(Arrays.asList(applicationContext.getBeanDefinitionNames()).toString());
				logger.debug("Looking mysqlDataSource from application context");
			}
			this.snowflakeDataSource = ((SnowflakeConfig) applicationContext.getBean("snowflakeConfig")).snowflakeDataSource();
		}
		return this.snowflakeDataSource;
	}
	
	public List<Object> executeSampleQuery() throws DaoException{
		Connection connection = null;
		try {
			connection = this.getSnowFlakeDataSource().getConnection();//jdbcTemplate.getDataSource().getConnection();
			String sql = "select * from wgtraffic limit 5";
			return this.getResults(sql, connection);
		} catch (Exception e) {
			logger.error("Exception while executing sample query", e);
			throw new DaoException(e);
		}
	}
	
	public List<List<Object>> executeQueries(List<String> queryList) throws DaoException{
	    List<List<Object>> responseList = new ArrayList<List<Object>>(queryList.size());
	    Connection connection = null;
        try {
    	    for (String query : queryList) {
    	        connection = this.getSnowFlakeDataSource().getConnection();
                responseList.add(this.getResults(query, connection));
            }
    	} catch (Exception e) {
            logger.error("Exception while executing query list", e);
            throw new DaoException(e);
        }
	    return responseList;
	}
	
	private List<Object> getResults(String query, Connection connection) throws DaoException {
		List<Object> resultList = new ArrayList<Object>();
		ResultSet resultSet = null;
//		System.out.println("Getting the query results");

		try {
			logger.debug(query);

			resultSet = connection.createStatement().executeQuery(query);
			ResultSetMetaData resultSetMetaData = resultSet.getMetaData();
			int columnCount = resultSetMetaData.getColumnCount();
			List<String> columnNames = new ArrayList<String>(columnCount);
			Map<String,Integer> columnTypes = new HashMap<String,Integer>(columnCount);
//			System.out.println("Executed the query to get resultset");

			for (int counter = 1; counter <= columnCount; counter++) {
				columnNames.add(resultSetMetaData.getColumnLabel(counter));
				columnTypes.put(resultSetMetaData.getColumnLabel(counter), resultSetMetaData.getColumnType(counter));
			}

			Map<String, Object> result = null;
			while (resultSet.next()) {
				result = new HashMap<String, Object>(columnCount);
				
				for (String columnName : columnNames) {
				    result.put(columnName, resultSet.getString(columnName));
				    /*if(columnTypes.get(columnName) == Types.INTEGER || columnTypes.get(columnName) == Types.SMALLINT || columnTypes.get(columnName) == Types.BIGINT) {
				        result.put(columnName, resultSet.getInt(columnName));
				    }else {
				        result.put(columnName, resultSet.getString(columnName));
				    }*/
				}
				resultList.add(result);
			}
			System.out.println("Executed query " + query + " going to close connection");
			resultSet.close();
			connection.close();
			System.out.println("Closed connection and resultSet");
		} catch (Exception e) {
			System.out.println("Exception in executing query");
			throw new DaoException(e);
		} finally {
			try {
				if (resultSet != null && !resultSet.isClosed()) {
					resultSet.close();
					System.out.println("Closing out resultset");
				}
				if (connection != null && !connection.isClosed()) {
					connection.close();
					System.out.println("Closing out connection");
				}
			} catch (SQLException e1) {
				System.out.println("SQLEXception in executing query");
				logger.error("Exception while closing connection", e1);
			}
		}
		return resultList;
	}
	
	 @Override
	  public String executeStoredProceedure(String sp) throws DaoException {
	        String result =  null;
	        ResultSet resultSet = null;
	        Connection connection = null;
	        try {
	            connection = this.getSnowFlakeDataSource().getConnection();//jdbcTemplate.getDataSource().getConnection();
	           //Uncomment
	            //CallableStatement cstmt = connection.prepareCall("call SP_ODM_HISTOGRAM_COUNT(?,?,?,?) ");
	            CallableStatement cstmt = connection.prepareCall(sp);
	            
	           // CallableStatement cstmt = connection.prepareCall("call SP_ODM_HISTOGRAM_COUNT_test1(?,?,?,?) ");
			/*
			 * cstmt.setString(1, " where "+whereCondition); cstmt.setString(2, bucketType);
			 * cstmt.setString(3, interval); cstmt.setString(4, viewName.trim());
			 * logger.info("view Name "+viewName); logger.info("WHERE "+whereCondition);
			 * logger.info("bucket "+bucketType); logger.info("interval "+interval);
			 */
	            resultSet = cstmt.executeQuery();
	           // Syste
	            System.out.println(resultSet.getFetchSize());
	            while(resultSet.next()) {
	                result = resultSet.getString(1);
	               // System.out.println("Result Print "+result);
	            }
	            //System.out.println(resultSet.getString("1"));
	            cstmt.close();
	            connection.close();
	            return result;
	        } catch (Exception e) {
	            logger.error("Exception while executing sample query", e);
	            throw new DaoException(e);
	        } finally {
	            try {
	                if (resultSet != null && !resultSet.isClosed()) {
	                    resultSet.close();
	                }
	                if (connection != null && !connection.isClosed()) {
	                    connection.close();
	                }
	            } catch (SQLException e1) {
	                logger.error("Exception while closing connection", e1);
	            }
	        }
	    }

    @Override
    public String executeAggregationQuery(String whereCondition, String bucketType, String interval, String viewName)
            throws DaoException {
        String result =  null;
        ResultSet resultSet = null;
        Connection connection = null;
        try {
            connection = this.getSnowFlakeDataSource().getConnection();//jdbcTemplate.getDataSource().getConnection();
           //Uncomment
            CallableStatement cstmt = connection.prepareCall("call SP_ODM_HISTOGRAM_COUNT(?,?,?,?) ");
           // CallableStatement cstmt = connection.prepareCall("call SP_ODM_HISTOGRAM_COUNT_test1(?,?,?,?) ");
            cstmt.setString(1, " where "+whereCondition);
            cstmt.setString(2, bucketType);
            cstmt.setString(3, interval);
            cstmt.setString(4, viewName.trim());
            logger.info("view Name "+viewName);
            logger.info("WHERE "+whereCondition);
            logger.info("bucket "+bucketType);
            logger.info("interval "+interval);
            resultSet = cstmt.executeQuery();
           // Syste
            System.out.println(resultSet.getFetchSize());
            while(resultSet.next()) {
                result = resultSet.getString(1);
               // System.out.println("Result Print "+result);
            }
            //System.out.println(resultSet.getString("1"));
            cstmt.close();
            connection.close();
            return result;
        } catch (Exception e) {
            logger.error("Exception while executing sample query", e);
            throw new DaoException(e);
        } finally {
            try {
                if (resultSet != null && !resultSet.isClosed()) {
                    resultSet.close();
                }
                if (connection != null && !connection.isClosed()) {
                    connection.close();
                }
            } catch (SQLException e1) {
                logger.error("Exception while closing connection", e1);
            }
        }
    }
    
    public List<Object> executeQuery(String sqlQuery) throws DaoException{
		Connection connection = null;
		try {
			connection = this.getSnowFlakeDataSource().getConnection();//jdbcTemplate.getDataSource().getConnection();
			//String sql = "select * from vw_odm_search limit 5";
			return this.getResults(sqlQuery, connection);
		} catch (Exception e) {
			logger.error("Exception while executing sample query", e);
			throw new DaoException(e);
		} finally {
			try {
				if (!connection.isClosed())
					connection.close();
			} catch (SQLException e1) {
					System.out.println("SQLEXception in executing query");
					logger.error("Exception while closing connection", e1);
			}
		}
	}
    
	public List<String> getColumnMetaData(String viewName) throws DaoException {
		//String query = "select * from "+viewName+" where ((EVENT_TIME >=  to_timestamp('2020-03-31T10:09:50.631Z'))  and (EVENT_TIME <=  to_timestamp('2020-03-01T10:09:50.631Z')) ) limit 1";
		String query = "show columns in "+viewName;
		ResultSet resultSet = null;
		Connection connection = null;
		Map<String,String> columnTypes = null;
		List<String> columnNames = new ArrayList<String>();
		try {
			connection = this.getSnowFlakeDataSource().getConnection();
			logger.debug(query);
			resultSet = connection.createStatement().executeQuery(query);			
			
			columnTypes = new HashMap<String, String>();;
			while (resultSet.next()) {
				
				columnTypes.put(resultSet.getString("column_name"),resultSet.getString("data_type"));
				
				columnNames.add(resultSet.getString("column_name"));
			}
			
			
			resultSet.close();
			connection.close();
			//return columnTypes;
		} catch (Exception e) {
			throw new DaoException(e);
		} finally {
			try {
				if (resultSet != null && !resultSet.isClosed()) {
					resultSet.close();
				}
				if (connection != null && !connection.isClosed()) {
					connection.close();
				}
			} catch (SQLException e1) {
				logger.error("Exception while closing connection", e1);
			}
		}
		
		return columnNames;

	}
}
