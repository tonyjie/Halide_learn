# How CodeGenerator Works
## void Func::compile_to_static_library (trace)
tutorial: lesson_10_aot_compilation_generate.cpp
```
brighter.compile_to_static_library("lesson_10_halide", {input, offset}, "brighter");    
```

```
pipeline().compile_to_static_library(filename_prefix, args, fn_name, target)    
{
    Module m = compile_to_module(args, fn_name, target);
    Outputs outputs = static_library_outputs(filename_prefix, target);
    m.compile(outputs);    
}
```

## Module Pipeline::compile_to_module(const vector<Argument> &args, const string &fn_name, const Target &target, const LinkageType linkage_type)
args = {input, offset}, fn_name = "brighter"
Internal::IntrusivePtr<PipelineContents> contents;  
contents是指向PipelineContents类对象的指针  

### PipeLineContents
初始化函数：
```
PipelineContents() :
    module("", Target()) {
    user_context_arg.arg = Argument("__user_context", Argument::InputScalar, type_of<const void*>(), 0, ArgumentEstimates{});
    user_context_arg.param = Parameter(Handle(), false, 0, "__user_context");
}
```    


lots of code to judge whether it's the same_compile compared to existing module (how is the existing module?)   
if it is: reuse old module  
else:
```
vector<IRMutator *> custom_passes;
for (CustomLoweringPass p : contents->custom_lowering_passes) {
    custom_passes.push_back(p.pass);
}
contents->module = lower(contents->outputs, new_fn_name, target, lowering_args,
                            linkage_type, contents->requirements, custom_passes);
```

### Module lower(...)
```
Module lower(const vector<Function> &output_funcs,
             const string &pipeline_name,
             const Target &t,
             const vector<Argument> &args,
             const LinkageType linkage_type,
             const vector<Stmt> &requirements,
             const vector<IRMutator *> &custom_passes)
```
Module result_module(simple_pipeline_name, t);  
lots of debug... is it something trivial?   

## Outputs static_library_outputs(const string &filename_prefix, const Target &target)
调用：  
```
Outputs outputs = static_library_outputs(filename_prefix, target);
```
filename_prefix = "lesson_10_halide"    

```
Outputs outputs = Outputs().c_header(filename_prefix + ".h");
outputs = outputs.static_library(filename_prefix + ".a");
```

### struct Outputs
A struct specifying a collection of outputs. Used as an argument to Pipeline::compile_to and Func::compile_to and Module::compile.  
    The functions are easy to understand.   
```
    Outputs c_header(const std::string &c_header_name) const {
        Outputs updated = *this;
        updated.c_header_name = c_header_name;
        return updated;
    }
```
```
    Outputs static_library(const std::string &static_library_name) const {
        Outputs updated = *this;
        updated.static_library_name = static_library_name;
        return updated;
    }
```

## void Module::compile(const Outputs &output_files_arg)    
调用：`m.compile(outputs);`     
```
std::unique_ptr<llvm::Module> llvm_module(compile_module_to_llvm_module(*this, context));
```
`compile_module_to_llvm_module()` call `codegen_llvm()`
`compile_llvm_module_to_object(*llvm_module, *out)` call `emit_file(module, out, llvm::TargetMachine::CGFT_ObjectFile)`: use a pass_manager to build up the passes that we want to do to the module.    
`pass_manager.run(*module);`: don't understand...   



