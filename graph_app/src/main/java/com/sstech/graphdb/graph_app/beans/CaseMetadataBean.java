package com.sstech.graphdb.graph_app.beans;

import java.util.Date;
import java.util.UUID;

public class CaseMetadataBean {
    private UUID uuid = null;
    private String caseName = null;
    private String status = null;
    private Date initiatedTime = new Date();
    private Date processingTime = new Date();

    public CaseMetadataBean(String name) {
        caseName = name;
    }

    public CaseMetadataBean setId(UUID id) {
        uuid = id;
        return this;
    }

    public CaseMetadataBean setStatus(String status) {
        this.status = status;
        return this;
    }

    public CaseMetadataBean setInitiatedTime(Date time) {
        initiatedTime = time;
        return this;
    }

    public CaseMetadataBean setProcessingTime(Date time) {
        processingTime = time;
        return this;
    }

    public String getCaseName() {
        return caseName;
    }

    public UUID getId() {
        return uuid;
    }

    public String getStatus() {
        return status;
    }

    public Date getInitiatedTime() {
        return initiatedTime;
    }

    public Date getProcessingTime() {
        return processingTime;
    }
}
