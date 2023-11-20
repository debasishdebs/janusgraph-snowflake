package com.sstech.graphdb.core.query;

import com.sstech.graphdb.core.query.utils.IdentifyQueryType;
import com.sstech.graphdb.grpc.InnerMostByteCode;
import com.sstech.graphdb.grpc.MiddleMostByteCode;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Properties;

public class TraversalStep {
    private final ArrayList<ArrayList<MiddleMostByteCode>> steps;
    private Integer stepIndex = 0;
    private MiddleMostByteCode root;
    private Integer hops = 0;
    private ResultSet result;
    private HashMap<Integer, String> directionPerHop = new HashMap<>();
    private ArrayList<String> rootFilter = new ArrayList<>();

    public TraversalStep(ArrayList<ArrayList<MiddleMostByteCode>> traversalStep, Integer index) {
        this.steps = traversalStep;
        stepIndex = index;
    }

    public TraversalStep withRoot(MiddleMostByteCode root) {
        this.root = root;
        return this;
    }

    private void generateRootFilters() throws Exception {

        for (InnerMostByteCode partStep : root.getMiddleLayerList()) {
            if (partStep.getInnerValues(0).equals("V") || partStep.getInnerValues(0).equals("E"))
                continue;

            if (partStep.getInnerValues(0).equals("T.label") || partStep.getInnerValues(0).equals("as"))
                throw new Exception("Doesn't yet support filter by label / assign to as");

            rootFilter.add(partStep.getInnerValues(0));
            rootFilter.add(partStep.getInnerValues(1));
        }
    }

    private void getEdgeDirectionPerHop() {
        for (java.lang.Integer i = 0; i < hops; i++) {
            ArrayList<MiddleMostByteCode> step = steps.get(i);
            
            String direction = new IdentifyQueryType(root).identifyEdgeType(step);
            
            directionPerHop.put(i+1, direction);

        }
    }

    private Connection getConnection() throws SQLException {

        Properties properties = new Properties();

        properties.put("user", "Debasish");        // replace "" with your user name
        properties.put("password", "Work@456");    // replace "" with your password
        properties.put("warehouse", "COMPUTE_WH");   // replace "" with target warehouse name
        properties.put("db", "SNOWFLAKE_GRAPH_TEST");          // replace "" with target database name
        properties.put("schema", "GRAPH_TEST");      // replace "" with target schema name
        properties.put("role", "SYSADMIN");
        String connectStr = "jdbc:snowflake://ik55883.east-us-2.azure.snowflakecomputing.com";

        return DriverManager.getConnection(connectStr, properties);
    }

    public ResultSet execute() throws Exception {
        generateHops();
        getEdgeDirectionPerHop();
        generateRootFilters();

        String rootType = new IdentifyQueryType(root).identify();

        if (rootType.contains("Traversal"))
            throw new Exception("Strange I got a Traversal step as root node?");

        if (rootType.equals("EdgeCentric"))
            throw new Exception("Currently doesn't support EdgeCentric queries");

//        for (java.lang.Integer i = 0; i < hops; i++) {
//
//        }
        Connection conn = getConnection();
        System.out.println("Connected");
        String query = getQueryForHop(hops);
        System.out.println("Query being executed is ");
        System.out.println(query + "\n\n");
        result = conn.createStatement().executeQuery(query);

        return result;
    }

    public ResultSet getResult() {
        return result;
    }

    private String getQueryForHop(Integer hop) {
        String query = "";
        if (hop == 1) {
            query = "select r.\"NODE_ID\"::string as srcId, r.\"LABEL\"::string as srcLabel , e1.value:id::string as outEdgeId , e1.value:label::string as outEdgeLabel , b.\"NODE_ID\"::string as targetId , b.\"LABEL\"::string as targetLabel  " +
                    " from nodes r, " +
                    " lateral flatten (r.\""+ directionPerHop.get(1) + "\") e1, " +
                    " lateral ( " +
                    "  select \"NODE_ID\", \"LABEL\" " +
                    "   from nodes " +
                    "   where \"NODE_ID\" = e1.value:target:id " +
                    "  ) as b " +
                    " where r.properties:" + rootFilter.get(0) + " = '" + rootFilter.get(1) + "';";
        }
        else if (hop == 2) {
            query = "select r.\"NODE_ID\"::string as aId , r.\"LABEL\"::string as aLabel , bn.bId::string as bId , bn.bLabel::string as bLabel , bn.cId::string as cId , bn.cLabel::string as cLabel  from nodes r, lateral flatten (r.\"" + directionPerHop.get(1) + "\") e1, lateral (select b.\"NODE_ID\" as bId, b.\"LABEL\" as bLabel, e2.value:target:id as cId, e2.value:target:label as cLabel from nodes b,  lateral flatten (b.\"" + directionPerHop.get(2) + "\") e2  where b.\"NODE_ID\" = e1.value:target:id  ) bn where r.properties:" + rootFilter.get(0) + " = '" + rootFilter.get(1) + "';";
        }
        else if (hop == 3) {
            query = "select r.\"NODE_ID\"::string as aId, r.\"LABEL\"::string as aLabel, bn.bId::string as bId, bn.bLabel::string as bLabel, bn.cId::string as cId, bn.cLabel::string as cLabel, bn.dId::string as dId, bn.dLabel::string as dLabel from nodes r, lateral flatten (r.\"" + directionPerHop.get(1) + "\") e1, lateral ( select b.\"NODE_ID\" as bId, b.\"LABEL\" as bLabel, cn.cId as cId, cn.cLabel as cLabel, cn.dId as dId, cn.dLabel as dLabel from nodes b, lateral flatten (b.\"" + directionPerHop.get(2) + "\") as e2, lateral ( select c.\"NODE_ID\" as cId, c.\"LABEL\" as cLabel, e3.value:target:id as dId, e3.value:target:label as dLabel from nodes c, lateral flatten (c.\"" +  directionPerHop.get(3) + "\") e3 where c.\"NODE_ID\" = e2.value:target:id ) cn  where b.\"NODE_ID\" in ( select e.value:target:id from nodes n, lateral flatten (n.\"" +  directionPerHop.get(1) + "\") e where n.properties:" + rootFilter.get(0) + " = '" + rootFilter.get(1) + "' ) ) bn where r.properties:" + rootFilter.get(0) + " = '" + rootFilter.get(1) + "';";
        }
        else if (hop == 4) {
            query = "select r.\"NODE_ID\"::string as aId, r.\"LABEL\"::string as aLabel, bn.bId::string, bn.bLabel::string, bn.cId::string, bn.cLabel::string, bn.dId::string, bn.dLabel::string, bn.eId::string, bn.eLabel::string " +
                    " from nodes r, " +
                    " lateral flatten (r.\"" +  directionPerHop.get(1) + "\") e1, " +
                    " lateral ( " +
                    "  // 1st level " +
                    "  select b.\"NODE_ID\" as bId, b.\"LABEL\" as bLabel, cn.cId, cn.cLabel, cn.dId, cn.dLabel, cn.eId, cn.eLabel " +
                    "   from nodes b, " +
                    "   lateral flatten (b.\"" +  directionPerHop.get(2) + "\") as e2, " +
                    "   lateral ( " +
                    "    // 2nd level " +
                    "    select c.\"NODE_ID\" as cId, c.\"LABEL\" as cLabel, dn.dId, dn.dLabel, dn.eId, dn.eLabel " +
                    "    from nodes c, " +
                    "    lateral flatten (c.\"" +  directionPerHop.get(3) + "\") e3, " +
                    "    lateral ( " +
                    "     // 3rd and 4th level " +
                    "     select d.\"NODE_ID\" as dId, d.\"LABEL\" as dLabel, e4.value:target:id as eId, e4.value:target:label as eLabel " +
                    "     from nodes d, " +
                    "     lateral flatten (d.\"" +  directionPerHop.get(4) + "\") e4 " +
                    "     where " +
                    "      d.\"NODE_ID\" = e3.value:target:id " +
                    "    ) dn " +
                    "    where c.\"NODE_ID\" in ( " +
                    "     select e.value:target:id " +
                    "      from nodes n1, " +
                    "      lateral flatten (n1.\"" +  directionPerHop.get(2) + "\") e " +
                    "      where n1.\"NODE_ID\" in ( " +
                    "        select e.value:target:id " +
                    "       from nodes n2, " +
                    "       lateral flatten (n2.\"" +  directionPerHop.get(1) + "\") e " +
                    "       where n2.properties:" + rootFilter.get(0) + " = '" + rootFilter.get(1) + "' " +
                    "      ) " +
                    "    ) " +
                    "   ) cn " +
                    "   where b.\"NODE_ID\" in ( " +
                    "              select e.value:target:id " +
                    "                from nodes n2, " +
                    "                lateral flatten (n2.\"" +  directionPerHop.get(1) + "\") e " +
                    "                where n2.properties:" + rootFilter.get(0) + " = '" + rootFilter.get(1) + "' " +
                    "            ) " +
                    " ) bn " +
                    " where r.properties:" + rootFilter.get(0) + " = '" + rootFilter.get(1) + "';";
        }

        return query;
    }

    private void generateHops() throws Exception {
        hops = steps.size();
        if (hops > 4)
            throw new Exception("Currently implemented traversal till depth of 4 for performance issue for " + hops.toString());

    }
}
