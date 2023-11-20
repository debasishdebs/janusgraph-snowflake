package com.sstech.graphdb.core.query;

import com.sstech.graphdb.grpc.ByteCode;
import com.sstech.graphdb.grpc.InnerMostByteCode;
import com.sstech.graphdb.grpc.MiddleMostByteCode;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import java.sql.ResultSet;
import java.util.ArrayList;

public class QueryExecutor {
    ByteCode byteCode;
    public QueryExecutor(ByteCode request) {
        byteCode = request;

        identifyTypeOfCentricQuery();
    }

    /*
    QueryExecutor is called with ByteCode
    QueryExecutor calls SplitQuery to split into collection of TraversalStep and ProjectMapStep
    StepExecutor is then called passing the collection of SplitQuery
    StepExecutor in turn calls TraversalExecutor and ProjectStepExecutor
    TraversalExecutor identifies if its EdgeCentric/VertexCentric/VertexTraversal/EdgeTraversal and executes it.

    VertexTraversalExecutor:
        Save the root vertex filter condition
        Identify if its out() or outE() based traversal. Save flag so that it can be used which generating SQL query
        Limit till hops < 5 for now.
        Generate 2 types of QueryGen function.
            1: Filter/Intersection of border nodes. Based on hop number it generate nested where condition till root node filter
            2: Property of nodes & edges in each level. This starts from root node and iteratively goes till outer node
        For every hop,
            1: Generate property for that level appended at begin
            2: Generate filter of border nodes appended at end
        Verify query & execute
     */

    public ArrayList<ResultSet> execute() throws Exception {
        SplitQuery queryMapper = new SplitQuery(byteCode);
        queryMapper.startSplit();
        ArrayList<TraversalStep> traversals = queryMapper.getTraversals();

        ArrayList<ResultSet> results = new ArrayList<>();
        for (TraversalStep traversal : traversals) {
            results.add(traversal.execute());
        }
        return results;
    }

    private void identifyTypeOfCentricQuery() {
        for (MiddleMostByteCode step : byteCode.getStepsList()) {
            for (InnerMostByteCode innerMostByteCode : step.getMiddleLayerList()) {
                ByteCodeParser parser = new ByteCodeParser(innerMostByteCode);

                if (parser.isEdgeCentricQuery())
                    throw new NotImplementedException();
            }
        }
    }

    private void stepExecutor() {
        for (MiddleMostByteCode step : byteCode.getStepsList()) {
            StepParser stepParser = new StepParser(step);
        }
    }
}
