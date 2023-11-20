package com.sstech.graphdb.core.query;

import com.sstech.graphdb.grpc.MiddleMostByteCode;

import java.util.ArrayList;

public class ProjectMapStep {
    ArrayList<MiddleMostByteCode> steps;
    public ProjectMapStep(ArrayList<MiddleMostByteCode> projectSteps) {
        steps = projectSteps;
    }

    public void execute() {

    }
}
