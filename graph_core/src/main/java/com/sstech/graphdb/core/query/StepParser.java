package com.sstech.graphdb.core.query;

import com.sstech.graphdb.grpc.InnerMostByteCode;
import com.sstech.graphdb.grpc.MiddleMostByteCode;

public class StepParser {
    MiddleMostByteCode step;
    public StepParser(MiddleMostByteCode step) {
        this.step = step;
    }

    public String getElementStep() {
        return step.getMiddleLayer(0).getInnerValues(0);
    }

    public boolean containsAsStep() {
        for (InnerMostByteCode prop : step.getMiddleLayerList()) {
            if (prop.getInnerValues(0).equals("as"))
                return true;
        }
        return false;
    }
}
