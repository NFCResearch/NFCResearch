function data = addSineWave(data, tx_fs, sinewave_fs)
    sine = dsp.SineWave(SamplesPerFrame=length(data), SampleRate=tx_fs, Frequency=sinewave_fs, ComplexOutput=1);
    sineData = sine();
    data = data.*sineData;
end