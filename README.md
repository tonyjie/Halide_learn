# Running CodeGen_C
在Halide/test下有internal.cpp文件，包含各种测试函数的调用。通过
```
g++ internal.cpp -std=c++11 -I ../src -L ../bin -lHalide -lpthread -ldl -o internal
./internal
```
跑了一遍代码，当然自己只显示xxx test passed

# some knowledge for C++
### 头文件加入 #ifndef/#define/#endif 防止重复编译出错的问题。  
格式： 
``` 
#ifndef <标识>    
#define <标识>  
......  
#endif  
```
每个头文件的<标示>应该是唯一的，命名规则一般是头文件名全大写，并把文件名中的"."也变成下划线 

### 匿名namespace
与static类似，匿名namespace内的变量只能在这个文件内访问，其他文件无法通过extern访问到   

### 嵌套的命名空间
```
namespace ns1{
    namespace ns2{

    }
}
```
  
### 类、枚举类型
class Rectangle: public Shape   
类的继承    
枚举类型：enum <类型名> {<枚举常量表>}; 

### 虚函数：    
在基类用virtual声明成员函数为虚函数。在类外定义虚函数时，不必再加virtual    
在派生类中重新定义此函数，要求函数名、函数类型、函数参数个数和类型全部与基类的虚函数相同，并根据派生类的需要重新定义函数体。  

C++11 中的 override 关键字，可以显式的在派生类中声明，哪些成员函数需要被重写，如果没被重写，则编译器会报错。

explicit关键字：防止类构造函数的隐式自动转换    

### R"name(string)name"
实际作用等于string，只是在string很长时括起来加个名字   

### 常引用：const 类型标识符 &引用名=目标变量名
例如 const int &ra=a;  
用这种方式声明的引用，不能通过引用对目标变量的值进行修改,从而使引用的目标成为const

### mutable 关键字
被mutable修饰的变量，将永远处于可变的状态，即使在一个const函数中。  

## 智能指针
对普通的指针进行封装，使得智能指针实质上是一个对象，行为表现得却像一个指针  
作用：防止忘记调用delete释放内存和程序异常的进入catch块忘记释放内存，可以解决指针释放时机的问题；把值语义转换成引用语义 

头文件 memory 中, 有shared_ptr, unique_ptr, weak_ptr
### shared_ptr    
shared_ptr多个指针指向相同的对象。shared_ptr使用引用计数，每一个shared_ptr的拷贝都指向相同的内存。每使用他一次，内部的引用计数加1，每析构一次，内部的引用计数减1，减为0时，自动删除所指向的堆内存。shared_ptr内部的引用计数是线程安全的，但是对象的读取需要加锁。   
智能指针类将一个计数器与类指向的对象相关联，引用计数跟踪该类有多少个对象共享同一指针。  
use_count()：检查shared_ptr对象的引用计数；这个值是shared_ptr指向的对象的引用次数，即如果两个shared_ptr指向同一对象，这两个shared_ptr.use_count()输出的值相等   

### C++ this指针
this指针是所有成员函数的隐含参数，在成员函数内部，this指针可以用来指向调用对象  

### extern "C"
提示编译器按照C的规则去翻译相应的函数名而不是按C++的

### name mangling 命名粉碎（命名重整）
C++可以实现方法重载，即同函数名加不同类型参数就可以实现不同功能。这种技术对于编译器来说是通过name mangling实现的：在这种技术中，编译器通过把原方法名称与其参数相结合产生一个独特的内部名字来取代原方法名称。

### Something About C Compile
.a:静态库 .so:动态库 .o:目标文件 .out:可执行文件 






















# CodeGen_C::test()
## Argument -> LoweredArgument
LoweredArgument(name,kind,type,dimensions,ArgumentEstimates)

### Kind: {InputScalar,InputBuffer|OutputBuffer}

enum Halide::Argument::Kind
An argument is either a primitive type (for parameters), or a
buffer pointer.

If kind == InputScalar, then type fully encodes the expected type
of the scalar argument.

If kind == InputBuffer|OutputBuffer, then type.bytes() should be used to determine* elem_size of the buffer; additionally, type.code *should* reflect the expected interpretation of the buffer data (e.g. float vs int), but there is no runtime enforcement of this at present.

Argument到底是啥，起什么作用

## Var
implicit:隐式创建时名字前加下划线：'_0','_1'...

## Param
A scalar parameter to a halide pipeline. If you're jitting, this should be bound to an actual value of type T using the set method before you realize the function uses this. If you're statically compiling, this param should appear in the argument list.    

## Expr -> Internal::IRHandle -> IntrusivePtr
A fragment of Halide syntax. It's implemented as reference-counted handle to a concrete expression node, but it's immutable, so you can treat it as a value type.   
似乎都是通过make来赋值  
IRHandle(const IRNode *p)

### IR.h: Add/Cast/Sub ... -> ExprNode -> BaseExprNode -> IRNode
IRNode: We use the visitor pattern to traverse IR nodes throughout the compiler, so we have a virtual accept method which accepts visitors. 
包含一个mutable RefCount ref_count: 应该是用于记录该IRNode对象被多少个指针指向。    
rtti: run-time type identification? 是什么意思? 


#### Expr Add::make(Expr a, Expr b)
函数返回值为一个Expr：其实就是一个指向结构体Add的指针，并给结构体Add的成员赋值：a和b为相加的两项（两个Expr),type与a.type相同（也与b.type相同），即int,float...等  

#### Expr Select::make(Expr condition, Expr true_value, Expr false_value)    

不同Expr的具体实现在哪里呢？Add在哪里Add了？Select在哪里Select了？————在IRPrinter的visit函数里

mutate？    

### Store -> StmtNode -> BaseStmtNode -> IRNode
store a 'value' to the buffer called 'name' at a given 'index' if 'predicate' is true. 

#### Stmt Store::make(const std::string &name, Expr value, Expr index,Parameter param, Expr predicate, ModulusRemainder alignment)





### LetStmt -> StmtNode -> BaseStmtNode -> IRNode
The statement form of a let node. Within the statement 'body', instances of the Var named 'name' refer to 'value'   



#### Stmt LetStmt::make(name, Expr value, Stmt body)
返回一个



......

### Variable -> ExprNode
make(type, name, Buffer<>(), Parameter(), ReductionDomain())

## Module
A halide module. This represents IR containing lowered function definitions and buffers. 

Module(const std::string &name, const Target &target);  
Target:目标架构：OS, Arch, 

Internal::IntrusivePtr<Internal::ModuleContents> contents;contents是一个ModuleContents类型的智能指针      

### IntrusivePtr.h
侵入式指针，智能指针,与shared_ptr类似（但还不清楚区别在哪，似乎就是IntrusivePtr需要自己写一些代码来记录引用次数）   
效果是指针可以自动释放，可以记录指向的对象同时被多少个指针指，当这个次数=0时，这片区域就可以自动释放了。    

### 初始化函数：Module::Module(name,target):
new了一个contents，contents->name = name; contents->target = target;    

### void append(const Internal::LoweredFunc &function)
contents->functions.push_back(funtion); 
contents->functions是contents指的一个vector，类型为LoweredFunc。这里在这个向量后push进新的function  
 

### ModuleContents
结构体，记录了ref_count, name, auto_schedule, buffers, functions, submodules, external_code, metadata_name_map  

### LoweredFunc
(string name, std::vector<LoweredArgument> args, Stmt body, LinkageType linkage)
对应于CodeGen_C::test()中的LoweredFunc("test1", args, s, LinkageType::External) 其中s为经过了很多次make的Stmt，args为vector<LoweredArgument>    

初始化函数：把name, Stmt body, linkage, name_mangling都赋值了，args向量中的每个LoweredArgument被push_back到对象对应的成员中（也是一个vector）   

LinkageType linkage 是什么？












# CodeGen_C -> IRPrinter -> IRVisitor 
Initialize a C code generator pointing at a particular output stream (e.g. a file, or std::cout)  

```  
    enum OutputKind {
        CHeader,
        CPlusPlusHeader,
        CImplementation,
        CPlusPlusImplementation,
    };
```
应该代表的是生成C代码的类型，在compile的时候会根据类型生成不同的代码    

## IRPrinter -> IRVisitor
### 初始化函数 IRPrinter(std::ostream &)
```
IRPrinter::IRPrinter(ostream &s) : stream(s), indent(0) {
    s.setf(std::ios::fixed, std::ios::floatfield);
}
```
indent: the current indentation level, useful for pretty-printing statements    
s.setf(std::ios::fixed, std::ios::floatfield); 这设置了cout对象的一个标记，命令cout使用定点表示法，避免科学计数法   
### IRPrinter::visit(const IntImm *) override
IRPrinter对于每种Expr,Stmt都有visit函数，函数里写了如何根据Expr/Stmt给stream赋值    
### IRPrinter::visit(const Add *) override
```
void IRPrinter::visit(const Add *op) {
    stream << '(';
    print(op->a);
    stream << " + ";
    print(op->b);
    stream << ')';
}
```
即输出 (Expr a + Expr b)

## IRVisitor
a base class for algorithms that need to recursively walk over the IR.  
### 各种visit函数
为虚函数。其中有些没有内容，有些包含这种语句：
```
op->a.accept(this);
op->b.accept(this);
```
op->a 和 op->b为Expr -> IRHandle -> IntrusivePtr, op(Add)为ExprNode -> BaseExprNode -> IRNode   

#### IRHandle::accept(IRVisitor *v) const {ptr -> accept(v);}
Dispatch to the correct visitor method for this node. E.g. if this node is actually an Add node, then this will call IRVisitor::visit(const Add *)  
按照注释说明的意思应该是：用于给这个节点调度正确的visitor method：如果是op是Add node就调用Add对应的visitor函数  
查看其definition发现是IRNode的accept纯虚函数    
accept的定义可以在ExprNode和StmtNode类的成员函数中找到：调用v->visit(this)  
```
template<> void ExprNode<IntImm>::accept(IRVisitor *v) const { v->visit((const IntImm *)this); }
```
 


### IRGraphVisitor -> IRVisitor
A base class for algorithms that walk recursively over the IR without visiting the same node twice. This is for passes that are capable of interpreting the IR as a DAG instead of a tree.  
(暂时没有看到哪个引用了这个类)  
visit函数只是包含了两个include函数
















## CodeGen_C初始化函数
CodeGen_C::test()中的调用：CodeGen_C cg(source, Target("host"), CodeGen_C::CImplementation);    
初始化函数：
```
CodeGen_C::CodeGen_C(ostream &s, Target t, OutputKind output_kind, const std::string &guard) :
    IRPrinter(s), id("$$ BAD ID $$"), target(t), output_kind(output_kind), extern_c_open(false)
```



## CodeGen_C::compile(Module &input)
Emit the declarations contained in the module as C code 
compile(const Module &module)   

前面TypeInfoGatherer的一通操作没有看懂，gpu什么的...... 
大概是：
f.body是Stmt类的对象，Stmt -> IRHandle -> IntrusivePtr  
defined()是IntrusivePtr的函数，查看指针是否定义。   
accept()是IRHandle的函数，但如前所述没搞懂是在干嘛  

f.args: LoweredArgument组成的向量   
forward_declare_type_if_needed(arg.type):
If the Type is a handle type, emit a forward-declaration for it if we haven't already.

如果不是header头文件的话：
    emit external-code blobs that are C++   
    add_vector_typedefs(type_info.vector_types_used)

    ExternalCallPrototypes e ......... 根据e有没有xxx declarations，调用一些函数，如set_name_mangling_mode(...) 还没有看懂  

```
for (const auto &b : input.buffers()) {
    compile(b);
}
for (const auto &f : input.functions()) {
    compile(f);
}
```
input是Module. 在test()中的Module似乎没有input.buffer()，只有input.functions    

### CodeGen_C::compile(const LowerFunc &f)
#### user_context
```
have_user_context = false;
for (size_t i = 0; i < args.size(); i++) {
    // TODO: check that its type is void *?
    have_user_context |= (args[i].name == "__user_context");
}
```
|=：位操作运算符，a|=b 等同于 a = a|b，按位或   
按照test()中的 args = { buffer_arg, float_arg, int_arg, user_context_arg }， 似乎have_user_context -> 0001 ??猜测   

#### name mangling
NameMangling类：enum class:{Default, C, CPlusPlus}  
分别对应{Match whatever is specified in the Target; No name mangling; C++ name mangling},默认为Default    

set_name_mangling_mode(name_mangling);  
似乎就是输入一些ifdef之类的东西 

#### namespaces
simple_name = extract_namespaces(f.name, namespaces); test()中的simple_name应该就是test1    
test()中的f.name = "test1"  

#### Emit the function prototype
先根据args列出 int test1()函数的参数    
print:关于__user_context的一个声明，不清楚__user_context是干嘛的？  

### print(f.body)
```
print(f.body)
```   

f.body是Stmt类的对象    

这里print函数为
```
void IRPrinter::print(Stmt ir) {
    ir.accept(this);
}
```
但是是IRPrinter的继承类CodeGen_C调用
即f.body.accept(CodeGen_C&), 相当于CodeGen_C::visit(f.body)

具体是怎么visit的？
需要看Stmt通过make的组织形式是怎样的...

从后往前看：

#### Call::make(Handle(),Call::buffer_get_host,{buf},Call::Extern)
函数定义：  
static Expr make(Type type, const std::string &name, const std::vector<Expr> &args, CallType call_type, FunctionPtr func = FunctionPtr(), int value_index = 0, Buffer<> image = Buffer<>(), Parameter param = Parameter());

其中Call::buffer_get_host = "_halide_buffer_get_host"   

这一句visit()会得到 _halide_buffer_get_host(_buf_buffer)  
这里本身括号里是输出Expr buf，但是buf由Variable::make生成，名字是buf.buffer(好像通过某种方式把.变成_,同时名字前加一个_) 

#### LetStmt::make("buf", Call::make(Handle(), Call::buffer_get_host, {buf}, Call::Extern), s)
LetStmt::make 返回的是一个Stmt，是一个指向LetStmt结构体的指针
函数定义：  
Stmt LetStmt::make(const std::string &name, Expr value, Stmt body)
```
void CodeGen_C::visit(const LetStmt *op) {
    string id_value = print_expr(op->value);
    Stmt body = op->body;
    if (op->value.type().is_handle()) {
        // The body might contain a Load or Store that references this
        // directly by name, so we can't rewrite the name.
        do_indent();
        stream << print_type(op->value.type())
               << " " << print_name(op->name)
               << " = " << id_value << ";\n";
    } else {
        Expr new_var = Variable::make(op->value.type(), id_value);
        body = substitute(op->name, new_var, body);
    }
    body.accept(this);
}
```
这里应该是进入了else中的部分，生成了临时新Var的名字，替换了原来的。然后这个过程还被body记录，调用accept应该就能通过visit打印出来这一段：void *_0 = ...; void * _buf = _0;

Q: IRMutator的作用还不太清楚？就是用来作这种替换么？    


#### Allocate::make("tmp.heap", Int(32), MemoryType::Heap, {43, beta}, const_true(), s);
```
static Stmt make(const std::string &name, Type type, MemoryType memory_type,
                const std::vector<Expr> &extents,
                Expr condition, Stmt body,
                Expr new_expr = Expr(), const std::string &free_function = std::string());
```

CodeGen_C::visit(const Allocate *op)    
第一个判断语句中进入else：
调用了两次print_assignment(); size_id = _2  
open_scope和close_scope指 { 和 }    
之后再调用halide_malloc (size_id = _3)
... 
op->body.accept(this) 这句话调用了前面其他的Stmt相应的visit函数 
最后close_scope

#### Block::make(s, Free::make("tmp.stack"))
结构体Free只有一个成员name  
CodeGen_C::visit(const Free *op)应该是完成一些对于allocations的操作     

Scope<Allocation> allocations   

这里应该没有打印什么东西

#### Allocate::make("tmp.stack", Int(32), MemoryType::Stack, {127}, const_true(), s)
```
static Stmt make(const std::string &name, Type type, MemoryType memory_type,
                const std::vector<Expr> &extents,
                Expr condition, Stmt body,
                Expr new_expr = Expr(), const std::string &free_function = std::string());
```
对应 int32_t _tmp_stack[127];

#### Block::make(s, Free::make("tmp.stack"))
同上 Block::make

#### LetStmt::make("x", beta+1, s)
对应 int32_t _4 = _beta + 1;

#### Store::make("buf", e, x, Parameter(), const_true(), ModulusRemainder());、
函数定义：
```
static Stmt make(const std::string &name, Expr value, Expr index,
                Parameter param, Expr predicate, ModulusRemainder alignment);
```
Store a 'value' to the buffer called 'name' at a given 'index' if 'predicate' is true. The buffer is interpreted as an array of the same type as 'value'. The name may be the name of an enclosing Allocate node, an output buffer, or any other symbol of type Handle().

Store的visit函数在调用过程中先有 
```
string id_value = print_expr(op_value);
```
其中print_expr中就调用了op_value的accept函数，即开始visit Expr e = Select::make(alpha > 4.0f, print_when(x < 1, 3), 2);     
调用完毕后有 ((int32_t *)_buf)[_4] = _13;

#### Select::make(alpha > 4.0f, print_when(x < 1, 3), 2)
Expr Select::make(Expr condition, Expr true_value, Expr false_value)

```
void CodeGen_C::visit(const Select *op) {
    ostringstream rhs;
    string type = print_type(op->type);
    string true_val = print_expr(op->true_value);
    string false_val = print_expr(op->false_value);
    string cond = print_expr(op->condition);

    // clang doesn't support the ternary operator on OpenCL style vectors.
    // See: https://bugs.llvm.org/show_bug.cgi?id=33103
    if (op->condition.type().is_scalar()) {
        rhs << "(" << type << ")"
            << "(" << cond
            << " ? " << true_val
            << " : " << false_val
            << ")";
    } else {
        rhs << type << "::select(" << cond << ", " << true_val << ", " << false_val << ")";
    }
    print_assignment(op->type, rhs.str());
}
```
先print_when(),对应于C_code的
```
   int32_t _5;
   bool _6 = _4 < 1;
   if (_6)
   {
    char b0[1024];
    snprintf(b0, 1024, "%lld%s", (long long)(3), "\n");
    char const *_7 = b0;
    int32_t _8 = halide_print(_ucon, _7);
    int32_t _9 = return_second(_8, 3);
    _5 = _9;
   } // if _6
   else
   {
    _5 = 3;
   } // if _6 else
```
再print_expr(op->condition)  (因为op->false_value=2,为一个数，没有特别的visit函数)  
对应于：
```
float _11 = float_from_bits(1082130432 /* 4 */);
bool _12 = _alpha > _11;
```
最后rhs被赋予(... ? ... : ...)的形式    
通过print_assignment()得到 int32_t _13 = (int32_t)(_12 ? _10 : 2);  








然后直接就 return 0了，大部分工作都是在print(f.body)完成的  
