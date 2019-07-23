# Lower.cpp: Module lower(...)
Schedule： split, reorder, fused, tile  
already be implemented in the initial loop nests.   
so need to trace some functions called before that...   

## populate_environment
### populate_environment_helper(f, env, true, true)
```
FindCalls calls
f.accept(&calls)
```
calls::calls为一个map<string, Function>， 存储着所有internal halide calls的name和func   
FindCalls为一个IRVisitor的继承类，可以find all the internal halide calls. 需要些其他Visitor时可以参照这个
```
env[f.name()] = f
```

### FunctionContents::FuncSchedule
a class, 包含的对象有： 
IntrusivePtr<FuncScheduleContents> contents;    
#### FuncScheduleContents
a struct. A schedule for a halide function, which defines where, when, and how it should be evaluated.  

## Realization_order
std::tie(order, fused_groups) = realization_order(outputs, env);    

### lhs, rhs?


## std::tie(outputs, env)   
应该是像tuple一样，就可以在函数return多个参数了 

## Stmt s = schedue_functions(outputs, fused_groups, env, t, any_memoized)
一开始是:
```
Stmt s = For::make(root_var, 0, 1, ForType::Serial, DeviceAPI::Host, Evaluate::make(0));
debug(1) << s << "\n";
```
显示：
```
for (.__root, 0, 1) {
  0
}
```

之后经过：
```
InjectFunctionRealization injector(funcs, is_output_list, target, env);
s = injector.mutate(s);
```
显示：
```
for (.__root, 0, 1) {
  produce output {
    let output.s0.y.loop_max = output.s0.y.max
    let output.s0.y.loop_min = output.s0.y.min
    let output.s0.y.loop_extent = ((output.s0.y.max + 1) - output.s0.y.min)
    let output.s0.x.loop_max = output.s0.x.max
    let output.s0.x.loop_min = output.s0.x.min
    let output.s0.x.loop_extent = ((output.s0.x.max + 1) - output.s0.x.min)
    let output.s0.__outermost.loop_extent = 1
    let output.s0.__outermost.loop_max = 0
    let output.s0.__outermost.loop_min = 0
    for (output.s0.__outermost, output.s0.__outermost.loop_min, output.s0.__outermost.loop_extent) {
      for (output.s0.x, output.s0.x.loop_min, output.s0.x.loop_extent) {
        for (output.s0.y, output.s0.y.loop_min, output.s0.y.loop_extent) {
          output(output.s0.x, output.s0.y) = (let output.s0.t0 = input(output.s0.x, output.s0.y) in (output.s0.t0 + output.s0.t0))
        }
      }
    }
  }
}
```

直接包括了reorder(y, x)的schedule信息   

### class InjectFunctionRealization : public IRMutator
经过trace和debug输出，主要讲function信息加入loop nest的步骤是： 
之前Stmt body输出为：
```
0
```

```
if (compute_level.match(for_loop->name)) {
    debug(1) << "Found compute level at " << for_loop->name << "\n";
    body = build_pipeline_group(body);
    _found_compute_level = true;
}
```

之后Stmt body输出为: (已有reorder schedule信息)
```
produce output {
  let output.s0.y.loop_max = output.s0.y.max
  let output.s0.y.loop_min = output.s0.y.min
  let output.s0.y.loop_extent = ((output.s0.y.max + 1) - output.s0.y.min)
  let output.s0.x.loop_max = output.s0.x.max
  let output.s0.x.loop_min = output.s0.x.min
  let output.s0.x.loop_extent = ((output.s0.x.max + 1) - output.s0.x.min)
  let output.s0.__outermost.loop_extent = 1
  let output.s0.__outermost.loop_max = 0
  let output.s0.__outermost.loop_min = 0
  for (output.s0.__outermost, output.s0.__outermost.loop_min, output.s0.__outermost.loop_extent) {
    for (output.s0.x, output.s0.x.loop_min, output.s0.x.loop_extent) {
      for (output.s0.y, output.s0.y.loop_min, output.s0.y.loop_extent) {
        output(output.s0.x, output.s0.y) = (let output.s0.t0 = input(output.s0.x, output.s0.y) in (output.s0.t0 + output.s0.t0))
      }
    }
  }
}
```

### Stmt build_pipeline_group(Stmt consume)
其中：
```
const Stmt &produceDef = build_produce_definition(f, f.name() + ".s0.", f.definition(), false,
                                                                  replacements, add_lets);
```
then:
```
Stmt produce = build_provide_loop_nest(env, prefix, f, def, (int)(start_fuse), is_update);
```
then:
```
Stmt stmt = build_loop_nest(body, prefix, start_fuse, func, def, is_update);
```
## here is the reorder 
stage_s = def.schedule(), 其中存放有reorder后的顺序 
```
for (int i = (int)stage_s.dims().size() - 1; i >= 0; i--) {
    const Dim &dim = stage_s.dims()[i];
    nest.emplace_back(Container::For, i, prefix + dim.var, Expr());
    debug(1) << dim.var << "\n";
}
```
打印出的顺序是：__outermost, x, y (for loop的顺序从外到内)  

trace back: def是class InjectFunctionRealization的对象funcs(vector<Function>)中一个元素的f的f.definition()

### IRMutator
同样有各种visit函数 
大概应该是继承类override IRMutator一些节点的visit函数，mutate时就会调用这些，利用make等改变Stmt的构成。完成在For Loop里inject之类的操作 


#### virtual Expr visit(const Add *)
return mutate_binary_operator(this, op);
#### Expr mutate_binary_operator(IRMutator *mutator, const T *op)
...


