import math


def num2tuple(num):
    return num if isinstance(num, tuple) else (num, num)


def conv2d_output_shape(h_w, kernel_size=1, stride=1, pad=0, dilation=1):
    h_w, kernel_size, stride, pad, dilation = num2tuple(h_w), \
                                              num2tuple(kernel_size), num2tuple(stride), num2tuple(pad), num2tuple(
        dilation)
    pad = num2tuple(pad[0]), num2tuple(pad[1])

    h = math.floor((h_w[0] + sum(pad[0]) - dilation[0] * (kernel_size[0] - 1) - 1) / stride[0] + 1)
    w = math.floor((h_w[1] + sum(pad[1]) - dilation[1] * (kernel_size[1] - 1) - 1) / stride[1] + 1)

    return h, w


def convtransp2d_output_shape(h_w, kernel_size=1, stride=1, pad=0, dilation=1, out_pad=0):
    h_w, kernel_size, stride, pad, dilation, out_pad = num2tuple(h_w), \
                                                       num2tuple(kernel_size), num2tuple(stride), num2tuple(
        pad), num2tuple(dilation), num2tuple(out_pad)
    pad = num2tuple(pad[0]), num2tuple(pad[1])

    h = (h_w[0] - 1) * stride[0] - sum(pad[0]) + dilation[0] * (kernel_size[0] - 1) + out_pad[0] + 1
    w = (h_w[1] - 1) * stride[1] - sum(pad[1]) + dilation[1] * (kernel_size[1] - 1) + out_pad[1] + 1

    return h, w


def conv2d_get_padding(h_w_in, h_w_out, kernel_size=1, stride=1, dilation=1):
    h_w_in, h_w_out, kernel_size, stride, dilation = num2tuple(h_w_in), num2tuple(h_w_out), \
                                                     num2tuple(kernel_size), num2tuple(stride), num2tuple(dilation)

    p_h = ((h_w_out[0] - 1) * stride[0] - h_w_in[0] + dilation[0] * (kernel_size[0] - 1) + 1)
    p_w = ((h_w_out[1] - 1) * stride[1] - h_w_in[1] + dilation[1] * (kernel_size[1] - 1) + 1)

    return (math.floor(p_h / 2), math.ceil(p_h / 2)), (math.floor(p_w / 2), math.ceil(p_w / 2))


def convtransp2d_get_padding(h_w_in, h_w_out, kernel_size=1, stride=1, dilation=1, out_pad=0):
    h_w_in, h_w_out, kernel_size, stride, dilation, out_pad = num2tuple(h_w_in), num2tuple(h_w_out), \
                                                              num2tuple(kernel_size), num2tuple(stride), num2tuple(
        dilation), num2tuple(out_pad)

    p_h = -(h_w_out[0] - 1 - out_pad[0] - dilation[0] * (kernel_size[0] - 1) - (h_w_in[0] - 1) * stride[0]) / 2
    p_w = -(h_w_out[1] - 1 - out_pad[1] - dilation[1] * (kernel_size[1] - 1) - (h_w_in[1] - 1) * stride[1]) / 2

    return (math.floor(p_h / 2), math.ceil(p_h / 2)), (math.floor(p_w / 2), math.ceil(p_w / 2))


if __name__ == "__main__":
    origin_shape = (200, 140)
    layer_shape1 = conv2d_output_shape(origin_shape, kernel_size=7, pad=3)
    layer_shape2 = conv2d_output_shape(layer_shape1, kernel_size=3, stride=2, pad=1)
    layer_shape3 = conv2d_output_shape(layer_shape2, kernel_size=3, stride=2, pad=1)
    layer_shape4 = conv2d_output_shape(layer_shape3, kernel_size=3, stride=2, pad=1)
    print(layer_shape1, layer_shape2, layer_shape3, layer_shape4)


    pad = convtransp2d_get_padding(layer_shape4, layer_shape3, kernel_size=3, stride=2)
    print(pad)
    pad = convtransp2d_get_padding(layer_shape3, layer_shape2, kernel_size=3, stride=2)
    print(pad)
    pad = convtransp2d_get_padding(layer_shape2, layer_shape1, kernel_size=3, stride=2)
    print(pad)
    pad = convtransp2d_get_padding(layer_shape1, origin_shape, kernel_size=7)
    print(pad)
