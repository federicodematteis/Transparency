void TurnOnCurve() {

    TFile file_in ("in.root", "READ");

    TF1* transparency_function_1 = new TF1 ("transparency_function_1", "[0]*exp(-[1]*x)+(1-[0])*exp([2]*x)");
    TF1* transparency_function_2 = new TF1 ("transparency_function_2", "[0]*exp(-[1]*(x-[3]))+(1-[0])*exp([2]*(x-[3]))");

    transparency_function_1->SetParameter(0, 9.93e-1);
    transparency_function_1->SetParameter(1, 3.87e-2);
    transparency_function_1->SetParameter(2, 3.22);

    transparency_function_2->SetParameter(0, 7.89);
    transparency_function_2->SetParameter(1, 2.71);
    transparency_function_2->SetParameter(2, -3.02);

    float delta_lumi_int = 0.05/2./2.;
    int n = 40*2;
    float max_lumi_int = delta_lumi_int*(n-1);
    double x[100], y[100];

    for (Int_t i=0;i<n;i++) {

        x[i] = i*delta_lumi_int;
        y[i] = transparency_function_1->Eval(x[i]);
    }

    TCanvas* cc_transp = new TCanvas ("cc_transp", "", 800, 600);

    TGraph* gr_tr = new TGraph(n,x,y);
    gr_tr->SetMarkerSize(1.);
    gr_tr->SetMarkerStyle(20);
    gr_tr->SetMarkerColor(kRed);
    gr_tr->Draw("APL");

    TCanvas* cc_turn_on = new TCanvas ("cc_turn_on", "", 800, 600);


    int nbin = 600;
    float min = 0;
    float max = 60;
    float delta_value = (max-min)/nbin;

    TH1F* h_turn_on = new TH1F ("h_turn_on", "", nbin, min, max);
    float threshold = 30;

    int nEvents = 1000;

    for (int ibin = 0; ibin<nbin; ibin++) {
        float value = min + (ibin+0.5)*delta_value;
            for (int iEvent = 0; iEvent < nEvents; iEvent++) {

                float lumi_int = gRandom->Uniform (0.7);
                float lumi_inst = gRandom->Uniform(0.0005);
                float lumi_inst_0 = gRandom->Uniform(0.0005);

                transparency_function_2->SetParameter(3, lumi_inst_0);

                float transparency = (transparency_function_1->Eval(lumi_int))*(transparency_function_2->Eval(lumi_inst));
                float value_smeared = value * transparency;

                if ( value_smeared > threshold) {
                    h_turn_on->Fill(value);
                }

            }

    }

    h_turn_on->Scale(1./nEvents);

    h_turn_on->SetLineWidth(2.);
    h_turn_on->SetLineColor(kRed);

    h_turn_on->Draw("histo");
    h_turn_on->GetXaxis()->SetTitle("Energy [GeV]");
    h_turn_on->GetYaxis()->SetTitle("Efficiency");

    TLine* vertical_line = new TLine (threshold, 0.0, threshold, 1.2);  
    vertical_line->SetLineColor(kBlue);
    vertical_line->SetLineWidth(2.0);
    vertical_line->Draw();

}
