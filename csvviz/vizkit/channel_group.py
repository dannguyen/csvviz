# class ChannelGroup(dict):

#     def __init__(self, **kwargs):
#         pass


#     def _create_channels(self) -> ChannelGroup:
#         def _set_default_xyvar_args(kargs) -> dict:
#             """
#             configure x and y channels, which default to 0 and 1-indexed column
#             if names aren't specified
#             """
#             cargs = kargs.copy()
#             for i, z in enumerate(("xvar", "yvar")):
#                 cargs[z] = cargs[z] if cargs.get(z) else self.column_names[i]
#             return cargs

#         def _validate_fieldname(shorthand: str, fieldname: str) -> bool:
#             if fieldname not in self.column_names:
#                 return False
#             else:
#                 return True

#         cargs = _set_default_xyvar_args(self.kwargs)
#         channels = {}

#         for n in ENCODING_CHANNEL_NAMES:
#             argname = f"{n}var"
#             vartxt = cargs.get(argname)  # walrus
#             if vartxt:  # e.g. 'name', 'amount|Amount', 'sum(amount)|Amount'  # /walrus
#                 shorthand, title = self.parse_channel_arg(vartxt)
#                 ed = self.parse_shorthand(shorthand, data=self.df)

#                 if _validate_fieldname(shorthand=shorthand, fieldname=ed["field"]):
#                     _channel = getattr(alt, n.capitalize())  # e.g. alt.X or alt.Y
#                     channels[n] = _channel(**ed)
#                     if title:
#                         channels[n].title = title
#                 else:
#                     raise InvalidDataReference(
#                         f"""'{shorthand}' is either an invalid column name, or invalid Altair shorthand"""
#                     )

#         ##################################
#         # subfunction: --color-sort, i.e. ordering of fill; only valid for area and bar charts
#         # somewhat confusingly, sort by fill does NOT alter alt.Fill, but adds an Order channel
#         # https://altair-viz.github.io/user_guide/encoding.html?#ordering-marks
#         _osort = cargs.get("fillsort")  # walrus
#         if _osort:  # /walrus
#             if not channels.get("fill"):
#                 raise MissingDataReference(
#                     f"--color-sort '{_osort}' was specified, but no --colorvar value was provided"
#                 )
#             else:
#                 # create an 'order' channel, with sort attribute
#                 fname = self.resolve_channel_name(channels["fill"])
#                 channels["order"] = alt.Order(fname)
#                 self.configure_channel_sort(channels["order"], _osort)

#         ##################################
#         # subfunction: set limits of x-axis and y-axis, via --xlim and --ylim
#         for i in (
#             "x",
#             "y",
#         ):
#             j = f"{i}lim"
#             limstr = cargs.get(j)  # walrus
#             if limstr:  # /walrus
#                 channels[
#                     i
#                 ].scale = (
#                     alt.Scale()
#                 )  # if channels[i].scale == alt.Undefined else channels[i].scale
#                 _min, _max = [k.strip() for k in limstr.split(",")]
#                 channels[i].scale.domain = [_min, _max]

#         return channels
