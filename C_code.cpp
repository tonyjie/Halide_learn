#ifndef HALIDE_FUNCTION_ATTRS
#define HALIDE_FUNCTION_ATTRS
#endif



#ifdef __cplusplus
extern "C" {
#endif

int test1(struct halide_buffer_t *_buf_buffer, float _alpha, int32_t _beta, void const *__user_context) HALIDE_FUNCTION_ATTRS {
 void * const _ucon = const_cast<void *>(__user_context);
 void *_0 = _halide_buffer_get_host(_buf_buffer);
 void * _buf = _0;
 {
  int64_t _1 = 43;
  int64_t _2 = _1 * _beta;
  if ((_2 > ((int64_t(1) << 31) - 1)) || ((_2 * sizeof(int32_t )) > ((int64_t(1) << 31) - 1)))
  {
   halide_error(_ucon, "32-bit signed overflow computing size of allocation tmp.heap\n");
   return -1;
  } // overflow test tmp.heap
  int64_t _3 = _2;
  int32_t *_tmp_heap = (int32_t  *)halide_malloc(_ucon, sizeof(int32_t )*_3);
  if (!_tmp_heap)
  {
   return halide_error_out_of_memory(_ucon);
  }
  HalideFreeHelper _tmp_heap_free(_ucon, _tmp_heap, halide_free);
  {
   int32_t _tmp_stack[127];
   int32_t _4 = _beta + 1;
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
   int32_t _10 = _5;
   float _11 = float_from_bits(1082130432 /* 4 */);
   bool _12 = _alpha > _11;
   int32_t _13 = (int32_t)(_12 ? _10 : 2);
   ((int32_t *)_buf)[_4] = _13;
  } // alloc _tmp_stack
  _tmp_heap_free.free();
 } // alloc _tmp_heap
 return 0;
}

#ifdef __cplusplus
}  // extern "C"
#endif

/*
void CodeGen_C::test() {
    LoweredArgument buffer_arg("buf", Argument::OutputBuffer, Int(32), 3, ArgumentEstimates{});
    LoweredArgument float_arg("alpha", Argument::InputScalar, Float(32), 0, ArgumentEstimates{});
    LoweredArgument int_arg("beta", Argument::InputScalar, Int(32), 0, ArgumentEstimates{});
    LoweredArgument user_context_arg("__user_context", Argument::InputScalar, type_of<const void*>(), 0, ArgumentEstimates{});
    vector<LoweredArgument> args = { buffer_arg, float_arg, int_arg, user_context_arg };
    Var x("x");
    Param<float> alpha("alpha");
    Param<int> beta("beta");
    Expr e = Select::make(alpha > 4.0f, print_when(x < 1, 3), 2);
    Stmt s = Store::make("buf", e, x, Parameter(), const_true(), ModulusRemainder());
    s = LetStmt::make("x", beta+1, s);
    s = Block::make(s, Free::make("tmp.stack"));
    s = Allocate::make("tmp.stack", Int(32), MemoryType::Stack, {127}, const_true(), s);
    s = Block::make(s, Free::make("tmp.heap"));
    s = Allocate::make("tmp.heap", Int(32), MemoryType::Heap, {43, beta}, const_true(), s);
    Expr buf = Variable::make(Handle(), "buf.buffer");
    s = LetStmt::make("buf", Call::make(Handle(), Call::buffer_get_host, {buf}, Call::Extern), s);

    Module m("", get_host_target());
    m.append(LoweredFunc("test1", args, s, LinkageType::External));

    ostringstream source;
    {
        CodeGen_C cg(source, Target("host"), CodeGen_C::CImplementation);
        cg.compile(m);
    }
*/