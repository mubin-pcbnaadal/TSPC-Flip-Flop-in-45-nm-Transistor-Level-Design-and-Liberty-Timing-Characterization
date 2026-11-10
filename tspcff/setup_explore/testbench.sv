// Testbench : setup time exploration of the TSPC D flip-flop
//
// D and CK logic signals rise at the same time, the CK electrical edge is
// delayed by clk_delay_val. Since D and CK have the same transition time
// (100ps), the delay between their 50% crossings is exactly clk_delay_val :
//      setup time = clk_delay_val
// For each setup time we measure the CK->Q rise propagation time (cell_rise).
// Fixed : CK slope 100ps, D slope 100ps, load 11fF
// Swept : setup time from 100ps down to 0ps by 10ps steps

`timescale 1ns/100fs

module testbench;

parameter real digital_tick    = 10  ;    // (ns)

// Logical signals
logic  din                ;
logic  clk                ;
wire   dout               ;
// Real signals to the board
real load_capacitor_val ;
real din_tt_val         ;
real clk_tt_val         ;
real din_delay_val      ;
real clk_delay_val      ;
// Real signal from the board
real cell_rise          ;

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

localparam NBSLOPES = 7 ;
localparam NBCAPA = 7 ;
localparam real slope_values[0:NBSLOPES-1] = '{0.001,0.015,0.03,0.045,0.06,0.08,0.10} ; // ns
localparam real capa_values[0:NBCAPA-1] = '{0.02,1.25,2.5,5,11,21,42}; // fF

// Setup time sweep : index 10 -> 0, step 10ps  (100ps -> 0ps)
localparam int  NBDELAY    = 11 ;
localparam real DELAY_STEP = 10.0e-12 ; // s

string outfilename ;
int outfile ;
integer STDERR = 32'h8000_0002;

initial
begin:simu
   int slope_index, capa_index, clk_delay_val_index ;
   real setup_time ;

   din_tt_val    = 0.10e-9 ;   // D transition time : 100ps
   din_delay_val = 0.0 ;
   clk_delay_val = 0.0 ;

   $swrite(outfilename,"results/TSPCFF_setup_explore.dat") ;
   outfile = $fopen(outfilename,"w") ;

   // Header : one line per setup time
   $fwrite(outfile,"setup(ns) cell_rise(ns) setup+cell_rise(ns)\n");

   din = 1'b0 ;
   clk = 1'b0 ;

   // Main loop : only the 0.10ns clock slope (index 6)
   for(slope_index=6;slope_index<7;slope_index++)
   begin
     #(digital_tick) ;
     clk_tt_val = slope_values[slope_index]*1.0e-9  ;

     // Secondary loop : only the 11fF load (index 4)
     for(capa_index=4;capa_index<5;capa_index++)
     begin
       load_capacitor_val = capa_values[capa_index]*1.0e-15  ;

       // Third loop : setup time from 100ps down to 0
       for(clk_delay_val_index=NBDELAY-1; clk_delay_val_index>=0; clk_delay_val_index--)
       begin
         clk_delay_val = clk_delay_val_index*DELAY_STEP ;
         setup_time    = clk_delay_val ;

         clk = 1'b0 ;            // clk and d to 0
         din = 1'b0 ;
         #(digital_tick) ;       // wait
         clk = 1'b1 ;            // store 0 in the flip-flop
         #(digital_tick) ;       // wait
         clk = 1'b0 ;            // clk to 0
         #(digital_tick) ;       // wait
         din = 1'b1 ;            // d and clk rise at the same time
         clk = 1'b1 ;            // (CK electrical edge delayed by clk_delay_val)
         #(digital_tick) ;       // wait

         if(dout !== 1'b1) begin
           // The flip-flop did not capture D=1 : setup time too short
           $fdisplay(STDERR,"\033[93m testbench: setup %0.1f ps : Q did not rise (capture failed) \033[0m", setup_time/1.0e-12) ;
           $fwrite(outfile,"%010.6f %010.6f %010.6f\n", setup_time/1.0e-9, -1.0, -1.0 ) ;
         end
         else begin
           $fwrite(outfile,"%010.6f %010.6f %010.6f\n", setup_time/1.0e-9, cell_rise/1.0e-9, (setup_time+cell_rise)/1.0e-9 ) ;
         end
       end
     end
   end
   $fclose(outfile) ;
   $stop ;
end

endmodule
