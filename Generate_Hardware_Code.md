# Generate HLS code
## Stencil
```
sodac stencil.soda --xocl-kernel stencil_kernel.cpp
```
failed:     
RecursionError: maximum recursion depth exceeded        

## Generate HLS code from SODA code
```
sodac ${app}.soda --xocl-kernel ${app}_kernel.cpp
```

## Run HLS code
```
source with-sdaccel  # Set environment
platform=xilinx_u200_qdma_201910_1
app=blur #blur is the name of program to be runned
xocc -t hw -f ${platform} --kernel ${app}_kernel --xp prop:kernel.${app}_kernel.kernel_flags="-std=c++0x" -c ${app}_kernel.cpp -o ${app}.hw.xo -s
```
Then find the .rpt file to see the resource & performance information     


