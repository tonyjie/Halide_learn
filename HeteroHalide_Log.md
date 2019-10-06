# HeteroHalide Log
to record all the function of Halide-to-HeteroCL Code Generator, and the overall flow and manual operation needed.

# Halide-to-HeteroCL Code Generator
Related files are CodeGen_HeteroCL.h and CodeGen_HeteroCL.cpp in the src folder of Halide. 

## Function defined in each Operation Node
### Variable
if found it in a map<string, Expr> inter_var, print the Expr; if didn't find it, print id   
inter_var is recorded in LetStmt node (haven't remembered what's the meaning yet)   

### IntImm
if type is Int(32), directly print the value; if type is others, print the type and bits, use "hcl.cast(dtype = hcl.Float(bits = ..., expr = ...))", for example.

### UIntImm
same as IntImm, use hcl.cast() to print dtype and bits information

### FloatImm
same as IntImm

### Cast
based on the cast_type, use hcl.cast() to print dtype and expr. Similar to the IntImm

### Add, Sub, Mul
call "visit_binop()" function with parameter Expr a, Expr b, const char * op    

#### visit_binop
if it is a normal operation, just print a, print op, print b    
But if it is involved with a reduction operation, Code Generator decides to print _sum(axis = ..., expr = ...) here. But it is not general, to be genral, we need to determine the scope using reduction domain index.      
** Current solution: just simply print reduction in the first operation: print a, print op, print reduction, print b    

### Max
max(a, b) is replaced with hcl.select: hcl.select(a > b, a, b)

### Min
min(a, b) is replaced with hcl.select: hcl.select(a < b, a, b)

### And
hcl.and_(a, b)

### Or
hcl.or_(a, b)

### Call
There are many call types, including Input, Intermediate Multi-dim Image, some function (pow_f32, exp_f32, absd...)

record map<string, vector\<int>>input_info. The key of the map is input name, value is input_extents.   

if it is some unique function (e.g. pow_f32), stream << hcl.power << print_list(op->args). 

If it is multi-dimensional Load: use function print_list_as_last_stage_order(op->args). This is to print the args (x, y, z, n) by the same order of the last stages. It is used to fix the reorder schedule. The last_func_axis_call_order is recorded in For node.

If it is call Input Image: use print_list_reverse(op->args) function. Because the default Halide IR axis order is opposite to the default HeteroCL axis order. 

### Select
nothing special. hcl.select(op->condition, op->true_value, false_value)

### Load
Don't use it for now. It is replaced by Call node for multi-dimensional load. Before, if the storage_flatten switch is opened, Halide IR use Load Node to load Image and Multi-dimensional Intermediate Image. 

### Store
Don't use it for now. It is replaced by Provide for multi-dimensional Store. Before, if the storage_flatten switch is opened, it is used for storing Image and Multi-dimensional Intermeidate Image.

### Let
Let node is like a group of recursive equations... Just print the equations one by one, and the last Let node's body is the return expr. 

### LetStmt
it is controlled by a bool variable: letstmt_validate. At first it is 0, to ignore lots of useless information. It's validated aftrer first Produce Node. 

Then, when it is enabled, every LetStmt record its op->name and op->value to the map inter_var. So this node doesn't print anything now. It only records inter_var.

Then it calls op->body.accept(this) to continue visiting further nodes. 

### AssertStmt
ignored

### ProducerConsumer
if is producer: get output_name. Record stage_num under each Producer Node. 

If is consumer: get consume_name, and record it in vector<string> consume_name_group

### For
If it is a reduction loop: record it in map<string, int> reduction_info. Key is the reduction domain loop, value is reduction index's extent.   

If it is a normal loop: record axis from the last char of op->min... For example, `for (f_conv.s0.n, output.min.3, output.extent.3)` we get the axis = 3 from the output.min.3  
(TODO: this is something need to be improved) Using current method, we can't support an Expr for op->min. Need another scheme to determine the axis of the stage.   

The use the information of axis, record it in vector<int> func_axis_call_order. 

For Unrolled type, we also record the information, and support it. For parallel or vectorize, I think we can use the same strategy.     
#### Judge the next node
If it is For node, continue 

If it is not For node, which means this node is the last For node:

print function hcl.compute()

### Provide
Used in Multi-Dimensional Store. 

Because Provide node appears before other nodes including Call (Multi-dimensional Load), so need to claim some information for Reduction here. 

If there are reduction_info, we decide to print "_sum = hcl.reducer(0, lambda x, y: x + y)", and "... = hcl.reduce_axis(0, ... )" here. 

Then print_list(op->values)

### Realize
to determine the output type of each stage. Because looking at Halide IR, I find that each realize node nearly corresponds to each produce node (a stage). But it's not for the last stage: only a Realize node, and 2 produce node (2 stages) under it. To make sure the output type is correct, we define a unnecessary stage: output = hw_output. 

Thus, the last two stages must have the same type.  

TODO: This can be set as a default schedule? : output = hw_output

### IfThenElse
op->then_case.accept(this);     

Don't show the condition, only show the then_case to continue...

It is for cleaning the code, have problems with its meaning

### Evaluate
op->value.accept(this)

Do nothing  