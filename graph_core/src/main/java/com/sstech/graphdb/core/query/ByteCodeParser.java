package com.sstech.graphdb.core.query;

import com.sstech.graphdb.grpc.InnerMostByteCode;

public class ByteCodeParser {
    private InnerMostByteCode code = null;
    public ByteCodeParser(InnerMostByteCode code) {
        this.code = code;
    }

    public boolean isVertexStep() {
        for (String s : code.getInnerValuesList()) {
            if (s.equals("V") || s.equals("otherV") || s.equals("inV") || s.equals("outV"))
                return true;
        }
        return false;
    }

    public boolean isVertexCentricQuery() {
        for (String s : code.getInnerValuesList()) {
            if (s.equals("V"))
                return true;
        }
        return false;
    }

    public boolean isEdgeCentricQuery() {
        for (String s : code.getInnerValuesList()) {
            if (s.equals("E"))
                return true;
        }
        return false;
    }

    public boolean isEdgeStep() {
        for (String s : code.getInnerValuesList()) {
            if (s.equals("E") || s.equals("bothE") || s.equals("outE") || s.equals("inE"))
                return true;
        }
        return false;
    }

    public boolean isProjectStep() {
        for (String s : code.getInnerValuesList()) {
            if (s.equals("project"))
                return true;
        }
        return false;
    }

    public boolean isSelectStep() {
        for (String s : code.getInnerValuesList()) {
            if (s.equals("select"))
                return true;
        }
        return false;
    }
}
