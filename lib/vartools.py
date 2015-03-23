# lib.vartools
# import hmac

secret = 'movethistoanimport'
#
# def make_secure_eval(val):
#     return '%s;%s' % (val, hmac.new(secret, val).hexdigest())
#
#
# def check_secure_eval(secure_val):
#     val = secure_val.split(';')[0]
#     if secure_val == make_secure_eval(val):
#         return val
#
#
# def render_post(response, post):
#     response.out.write('<b>' + post.subject + '</b><br>')
#     response.out.write(post.content)
