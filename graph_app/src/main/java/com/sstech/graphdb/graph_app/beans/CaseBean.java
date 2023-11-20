package com.sstech.graphdb.graph_app.beans;

import java.util.Date;

public class CaseBean {
    private Date startDate = null;
    private Date endDate = null;
    private String caseInformation = null;

    public CaseBean(String caseName) {
        caseInformation = caseName;
    }

    public void setStartDate(Date startDate) {
        this.startDate = startDate;
    }

    public void setEndDate(Date endDate) {
        this.endDate = endDate;
    }

    public Date getEndDate() {
        return endDate;
    }

    public Date getStartDate() {
        return startDate;
    }

    public String getCaseInformation() {
        return caseInformation;
    }

    @Override
    public String toString() {
        return String.format("CaseInfo: %s StartDate: %s EndDate: %s", caseInformation, startDate, endDate);
    }
}
