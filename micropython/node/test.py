from tin import Metric, PayloadIn, PayloadOut
m = Metric("test",3,3,12345)
p_out = PayloadOut(0,"uuid",12345)
p_out.add_metric(m)
buff = p_out.to_bytes()
p_in = PayloadIn(buff)

