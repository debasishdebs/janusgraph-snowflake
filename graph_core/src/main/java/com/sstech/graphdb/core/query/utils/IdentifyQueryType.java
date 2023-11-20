package com.sstech.graphdb.core.query.utils;

import com.sstech.graphdb.grpc.MiddleMostByteCode;

import java.util.ArrayList;
import java.util.IdentityHashMap;

public class IdentifyQueryType {
    private MiddleMostByteCode step;
    public IdentifyQueryType(MiddleMostByteCode step) {
        this.step = step;
    }

    public String identify() {
        if (step.getMiddleLayer(0).getInnerValues(0).equals("E"))
            return "EdgeCentric";

        if (step.getMiddleLayer(0).getInnerValues(0).equals("V"))
            return "VertexCentric";

        if (step.getMiddleLayer(0).getInnerValues(0).contains("V"))
            return "VertexTraversal";

        if (step.getMiddleLayer(0).getInnerValues(0).contains("E"))
            return "EdgeTraversal";

        return "NA";
    }

    public String identifyEdgeType(ArrayList<MiddleMostByteCode> step) {

        if (step.size() == 1) {
            if (step.get(0).getMiddleLayer(0).getInnerValues(0).equals("both"))
                return "bothEdges";

            if (step.get(0).getMiddleLayer(0).getInnerValues(0).equals("out"))
                return "outEdges";

            if (step.get(0).getMiddleLayer(0).getInnerValues(0).equals("in"))
                return "inEdges";
        }

        else {
            if (step.get(0).getMiddleLayer(0).getInnerValues(0).equals("bothE"))
                return "bothEdges";

            if (step.get(0).getMiddleLayer(0).getInnerValues(0).equals("outE"))
                return "outEdges";

            if (step.get(0).getMiddleLayer(0).getInnerValues(0).equals("inE"))
                return "inEdges";
        }
        return "NA";
    }
}
