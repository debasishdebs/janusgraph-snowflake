package com.sstech.graphdb.graph_app.beans;

import java.util.ArrayList;

public class DummyMessageBean {
    private String message;
    private String source;
    private String status;
    private ArrayList<String> currents = new ArrayList<>();


    public DummyMessageBean() {
    }

    public DummyMessageBean setMessage(String msg) {
        message = msg;
        return this;
    }

    public DummyMessageBean setSource(String source) {
        this.source = source;
        return this;
    }

    public DummyMessageBean setStatus(String status) {
        this.status = status;
        return this;
    }

    public DummyMessageBean addCurrent(String curr) {
        currents.add(curr);
        return this;
    }

    public DummyMessageBean setCurrent(String curr) {
        currents.add(curr);
        return this;
    }

    public String getMessage() {
        return message;
    }

    public String getSource() {
        return source;
    }

    public String getStatus() { return status; }

    public ArrayList<String> getCurrents() {
        return currents;
    }

    public String toString() {
        String msg = String.format("{Message: %s, Status: %s, Source: %s, Currents [%s]}",
                message, status, source, String.join(",", currents));
        return msg;
    }
}
