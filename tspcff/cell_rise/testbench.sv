// The testbench for the CK->Q timing measurement of a TSPC D flip-flop
// This code is purely digital code, using SystemVerilog language.
// This code mimics what can be done with a real breadboard using
// signal generators and oscilloscopes.
//
// Measurement : cell_rise = propagation time from CK rising (50%) to Q rising (50%)
// Swept parameters : CK transition time (clk_tt_val) and output load capacitor
// Fixed            : D transition time = 10ps, no extra delays

`timescale 1ns/100fs

module testbench;

// Time between two events on the DUT inputs (ns).
parameter real digital_tick    = 10  ;

// Logical signals
logic  din                ; // The logic D input of the flip-flop
logic  clk                ; // The logic CK input of the flip-flop
wire   dout               ; // The logic Q output of the flip-flop
// Real signals used to send values to the breadboard
real load_capacitor_val ; // The chosen value of the load capacitor on Q
real din_tt_val         ; // The chosen transition time of the D input
real clk_tt_val         ; // The chosen transition time of the CK input
real din_delay_val      ; // An arbitrary incremental delay added to the D input transition
real clk_delay_val      ; // An arbitrary incremental delay added to the CK input transition
// Real signals used to receive measured values from the breadboard
real cell_rise          ; // The measured CK->Q propagation time for a rising output

// Breadboard instanciation, using connected signals
board bdut(
                          .din_logic(din),
                          .clk_logic(clk),
                          .dout_electrical(dout),
                          .din_tt_val(din_tt_val),
                          .clk_tt_val(clk_tt_val),
                          .din_delay_val(din_delay_val),
                          .clk_delay_val(clk_delay_val),
                          .load_capacitor_val(load_capacitor_val),
                          .cell_rise(cell_rise)
                          ) ;

// The list of measurement points.
// The clock transition time must not exceed the max clock transition of the project : 100ps
localparam NBSLOPES = 7 ;
localparam NBCAPA = 7 ;
localparam real slope_values[0:NBSLOPES-1] = '{0.001,0.015,0.03,0.045,0.06,0.08,0.10} ; // ns (CK transition time)
localparam real capa_values[0:NBCAPA-1] = '{0.02,1.25,2.5,5,11,21,42}; // fF

// Defines a file name for storing output results
string outfilename ;
// Define a file pointer for the file.
int outfile ;
// Define the standard error channel.
integer STDERR = 32'h8000_0002;

// Reference model of the flip-flop, used to check the DUT output
logic dout_ref ;
always @(posedge clk)
    dout_ref <= din ;

initial
begin:simu
   int slope_index,capa_index ;

   // Fixed values for this measurement
   din_tt_val    = 10.0e-12 ; // D transition time : 10ps
   din_delay_val = 0.0 ;
   clk_delay_val = 0.0 ;

   // The output file
   $swrite(outfilename,"results/TSPCFF_cell_rise.dat") ;

   // Open the file for writing
   outfile = $fopen(outfilename,"w") ;

   // Write parameter infos on the first line of the resulting file
   $fwrite(outfile,"clk_slope(ns) ");
   for(capa_index=0;capa_index<NBCAPA;capa_index++)
   $fwrite(outfile,"ldcap(ff)  cell_rise(ns) ");
   $fwrite(outfile,"\n") ;

   // At time 0 inputs are initialized to 0
   din = 1'b0 ;
   clk = 1'b0 ;

   // Main loop on the CK slopes
   for(slope_index=0;slope_index<NBSLOPES;slope_index++)
   begin
     // We wait one tick in order to be sure that the DUT is "quiet"
     #(digital_tick) ;

     // Then we update the value of the clock slope
     clk_tt_val = slope_values[slope_index]*1.0e-9  ;
     // And we write the slope value in the file
     $fwrite(outfile,"%010.6f ",slope_values[slope_index] ) ;

     // Secondary loop on the output load capacitor
     for(capa_index=0;capa_index<NBCAPA;capa_index++)
     begin
       // Update the value of the load capacitor and write it in the file
       load_capacitor_val = capa_values[capa_index]*1.0e-15  ;
       $fwrite(outfile,"%010.6f ", capa_values[capa_index] ) ;

       // 1. clk and d to 0
       clk = 1'b0 ;
       din = 1'b0 ;
       // 2. wait for stable signals
       #(digital_tick) ;
       // 3. clk to 1 : store 0 in the flip-flop
       clk = 1'b1 ;
       // 4. wait for stable signals
       #(digital_tick) ;
       // 5. clk to 0
       clk = 1'b0 ;
       // 6. wait for stable signals
       #(digital_tick) ;
       // 7. d to 1
       din = 1'b1 ;
       // 8. wait for stable signals
       #(digital_tick) ;
       // 9. clk to 1 : Q rises (measured edge)
       clk = 1'b1 ;
       // 10. wait for stable signals
       #(digital_tick) ;

       // Then check if we have an expected value (flip-flop behaviour)
       if(dout != dout_ref) begin
           $fdisplay(STDERR,"\033[91m testbench: at time %0t: din:%0d, clk:%0d, dout:%0d, expected dout:%0d \033[0m", $realtime,din,clk,dout,dout_ref) ;
           $fdisplay(STDERR,"\033[92m testbench: ERROR detected from testbench\033[0m" ) ;
           $fflush(STDERR) ;
           $fflush(outfile) ;
           $finish ;
       end

       // Then we get the measured CK->Q propagation time for a rising output
       // and write it to the file
       $fwrite(outfile,"%010.6f ",cell_rise/1.0e-9 ) ;
     end
     $fwrite(outfile,"\n") ;
   end
   $fclose(outfile) ;
   $stop ;
end

endmodule
