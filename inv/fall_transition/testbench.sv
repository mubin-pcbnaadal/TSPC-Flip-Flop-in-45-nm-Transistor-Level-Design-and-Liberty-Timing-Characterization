// The testbench for the timing measurement of an invertor
// This code is purely digital code, using SystemVerilog language.
// This code mimics what can be done with a real breadboard using
// signal generators and oscilloscopes.

`timescale 1ns/100fs

module testbench;

// The testbench will generate "events" for the breadboard. We define here the time interval
// between two events. The time interval should be long enough to be sure that the DUT (Device
// Under Test) signals are stable when a measurement is asked to the breadboard.
// Warning: a two long time interval may lead to very slow simulations...
parameter real digital_tick    = 10  ;    // (ns) Time between two events on the DUT inputs.

// Logical signals
logic  din                ; // The logic input of the invertor.
wire dout                 ; // The logic output of the invertor
// Real signals used send values to the breadboard 
real load_capacitor_val ; // The choosen value of a load capacitor loading the output of the invertor
real tt_val             ; // The choosen value of the transition time of the input
real delay_val = 0.0    ; // An arbitrary incremental delay added to the input transition
// Real signals used receive measured values from the breadboard 
real fall_transition   ; // The measured output transition time for a falling output

// Breadboard instanciation, using connected signals
board bdut(
                          .din_logic(din), 
                          .dout_electrical(dout),
                          .tt_val(tt_val),
                          .delay_val(delay_val),
                          .load_capacitor_val(load_capacitor_val),
                          .fall_transition(fall_transition)
                          ) ;

// The list of measurement points is defined by 2 parameters tables extracted from the Liberty 
// files of the gcslib045 library.
// The input slope should no excess the max_input_transition of the library : 200ps
localparam NBSLOPES = 7 ;
localparam NBCAPA = 7 ;
localparam real slope_values[0:NBSLOPES-1] = '{0.001,0.03,0.07,0.10,0.13,0.17,0.20} ; // ns
localparam real capa_values[0:NBCAPA-1] = '{0.02,1.25,2.5,5,11,21,42}; // fF

// Defines a file name for storing output results
string outfilename ;
// Define a file pointer for the file.
int outfile ;
// Define the standard error channel.
integer STDERR = 32'h8000_0002;

initial 
begin:simu
   int slope_index,capa_index ;

   // The ouput file
   $swrite(outfilename,"measurements.dat") ;

   // Open the file for writing
   outfile = $fopen(outfilename,"w") ;

   // Write parameter infos on the first line of the resulting file
   $fwrite(outfile,"islope(ns) ");
   for(capa_index=0;capa_index<NBCAPA;capa_index++) 
   $fwrite(outfile,"ldcap(ff)  o_fall(ns) ");
   $fwrite(outfile,"\n") ;

   // At time 0 input is initialized to 0
   din = 1'b0 ;

   // Main loop on the din slopes
   for(slope_index=0;slope_index<NBSLOPES;slope_index++) 
   begin
     // We wait on tick in order to be sure that the DUT is "quiet"
     #(digital_tick) ; 

     // Then we update the value of the input slope
     tt_val = slope_values[slope_index]*1.0e-9  ;
     // And we write the slope value in the file
     $fwrite(outfile,"%010.6f ",slope_values[slope_index] ) ;

     // Secondary loop on the output load capacitor
     for(capa_index=0;capa_index<NBCAPA;capa_index++) 
     begin
       // We wait on tick in order to be sure that the DUT is "quiet"
       #(digital_tick) ; 

       // Then we update the value of the input slope
       load_capacitor_val = capa_values[capa_index]*1.0e-15  ;

       // And we write the capacitor value in the file
       $fwrite(outfile,"%010.6f ", capa_values[capa_index] ) ;

       // Then we wait on tick in order to be sure that the DUT is "quiet"
       #(digital_tick) ;

       // Then we generate a rising event on din
       din = 1'b1 ;

       // Then we wait on tick in order to be sure that the DUT is "quiet"
       #(digital_tick) ;

       // Then check if we have an expected value
       // For an invertor it is simply not(din) 
       if(dout != !din) begin
           $fdisplay(STDERR,"\033[91m testbench: at time %0t: din:%0d, dout:%0d \033[0m", $realtime,din,dout) ;
           $fdisplay(STDERR,"\033[92m testbench: ERROR detected from testbench\033[0m" ) ;
           $fflush(STDERR) ;
           $fflush(outfile) ;
           $finish ;
       end

       // Then we get the measured propagation time for a falling output as well as the transition time
       // and write it to the file
       $fwrite(outfile,"%010.6f ",fall_transition/1.0e-9 ) ;

       // Then we wait on tick in order to be sure that the DUT is "quiet"
       #(digital_tick) ;

       // Then we reset the din input
       din = 1'b0 ;
     end
     $fwrite(outfile,"\n") ;
   end
   $fclose(outfile) ;
   $stop ;
end

endmodule
