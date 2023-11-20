package com.sstech.graphdb.graph_app.beans;

import java.util.List;

public class EntityTypeQueryBean {
    private List<EntityQueryBean> entityQueries;

    public List<EntityQueryBean> getEntityQueries() {
        return entityQueries;
    }

    public void setEntityQueries(List<EntityQueryBean> entityQueries) {
        this.entityQueries = entityQueries;
    }
}
