package com.sstech.graphdb.graph_app.beans;


public class CaseExportPayloadBean {
    private EntityTypeQueryBean IP;
    private EntityTypeQueryBean user;
    private EntityTypeQueryBean hosts;
    private EntityTypeQueryBean URLs;
    private EntityTypeQueryBean processes;
    private EntityTypeQueryBean childProcesses;
    private EntityTypeQueryBean emails;

    public void setHosts(EntityTypeQueryBean hosts) {
        this.hosts = hosts;
    }

    public void setIP(EntityTypeQueryBean IP) {
        this.IP = IP;
    }

    public void setURLs(EntityTypeQueryBean URLs) {
        this.URLs = URLs;
    }

    public void setUser(EntityTypeQueryBean user) {
        this.user = user;
    }

    public void setChildProcesses(EntityTypeQueryBean childProcesses) {
        this.childProcesses = childProcesses;
    }

    public void setEmails(EntityTypeQueryBean emails) {
        this.emails = emails;
    }

    public void setProcesses(EntityTypeQueryBean processes) {
        this.processes = processes;
    }

    public EntityTypeQueryBean getIP() {
        return IP;
    }

    public EntityTypeQueryBean getHosts() {
        return hosts;
    }

    public EntityTypeQueryBean getURLs() {
        return URLs;
    }

    public EntityTypeQueryBean getUser() {
        return user;
    }

    public EntityTypeQueryBean getChildProcesses() {
        return childProcesses;
    }

    public EntityTypeQueryBean getEmails() {
        return emails;
    }

    public EntityTypeQueryBean getProcesses() {
        return processes;
    }
}
