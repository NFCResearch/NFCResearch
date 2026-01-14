file = ".\Data\OneSubcarrierLowDataRate\Card1.mat";
load(file);
    
scope = timescope();
scope2 = timescope();
scope3 = timescope();

scope(abs(command_data));
