package com.sstech.graphdb.graph_app.beans;

import java.util.Date;

public class EntityQueryBean {
    private String value;
    private String dataSource;

    private Date startDate;
    private Date endDate;

    public void setStartDate(Date startDate) {
        this.startDate = startDate;
    }

    public void setDataSource(String dataSource) {
        this.dataSource = dataSource;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public void setEndDate(Date endDate) {
        this.endDate = endDate;
    }

    public String getDataSource() {
        return dataSource;
    }

    public Date getStartDate() {
        return startDate;
    }

    public Date getEndDate() {
        return endDate;
    }

    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return String.format("EntityQueryBean{value=%s, dataSource=%s, startDate=%s, endDate=%s}",
                value, dataSource, startDate, endDate);
    }
}
