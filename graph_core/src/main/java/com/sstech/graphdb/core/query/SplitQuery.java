package com.sstech.graphdb.core.query;

import com.sstech.graphdb.grpc.ByteCode;
import com.sstech.graphdb.grpc.InnerMostByteCode;
import com.sstech.graphdb.grpc.MiddleMostByteCode;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class SplitQuery {
    private List<MiddleMostByteCode> steps;
    private ArrayList<MiddleMostByteCode> projectStepList = new ArrayList<>();
    private HashMap<MiddleMostByteCode, ArrayList<ArrayList<MiddleMostByteCode>>> traversals = new HashMap<>();

    public SplitQuery(ByteCode query) {
        steps = query.getStepsList();
    }

    public void startSplit() throws IllegalAccessException {

        for (MiddleMostByteCode step : steps) {
            InnerMostByteCode operation = step.getMiddleLayer(0);
            String centric = operation.getInnerValues(0);
            if (centric.equals("V") || centric.equals("E"))
                traversals.put(step, new ArrayList<>());
        }

        for (int i = 0; i < steps.size(); i++) {
            MiddleMostByteCode centric = steps.get(i);
            if (traversals.containsKey(centric)) {
                for (int j = i+1; j < steps.size(); j++) {
                    String rootStep = steps.get(j).getMiddleLayer(0).getInnerValues(0);

                    if (rootStep.equals("V") || rootStep.equals("E")) {
                        i = j;
                        break;
                    }

                    if (rootStep.equals("out") || rootStep.equals("in") || rootStep.equals("both")) {
                        ArrayList<ArrayList<MiddleMostByteCode>> existingSteps = traversals.get(centric);
                        ArrayList<MiddleMostByteCode> wrapper = new ArrayList<>();
                        wrapper.add(steps.get(j));
                        wrapper.add(steps.get(j+1));
                        existingSteps.add(wrapper);
                        traversals.put(centric, existingSteps);
                        j+= 1;
                    }
                    else {
                        ArrayList<ArrayList<MiddleMostByteCode>> existingSteps = traversals.get(centric);
                        ArrayList<MiddleMostByteCode> hopStep = new ArrayList<>();
                        hopStep.add(steps.get(j));
                        hopStep.add(steps.get(j+1));

                        existingSteps.add(hopStep);
                        traversals.put(centric, existingSteps);

                        j += 1;
                    }
                }
            }
        }

        for (MiddleMostByteCode step : steps) {
            InnerMostByteCode operation = step.getMiddleLayer(0);

            if (operation.getInnerValues(0).equals("project")) {
                if (traversals.size() == 0)
                    throw new IllegalAccessException("Project called before traversing graph. Illegal usage");

                projectStepList.add(step);
            }
        }
    }

    public ProjectMapStep getProjectSteps() {
        return new ProjectMapStep(projectStepList);
    }

    public ArrayList<TraversalStep> getTraversals() {
        Integer i = 1;
        ArrayList<TraversalStep> traversalSteps = new ArrayList<>();
        this.traversals.forEach( (root, steps) -> {
            traversalSteps.add(new TraversalStep(steps, i).withRoot(root));
        });
        return traversalSteps;
    }
}
