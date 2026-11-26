# Package and CSS

engine/__init__.py is empty; bridge/__init__.py is a docstring. pipeline/__init__.py adds pipeline path to sys.path if absent and exports BlueLine, ScaleStrike, count_scale_strikes, detect_blue_lines, fibonacci_level. CSS (960 lines in previous manifest) owns presentation for inspector, pin, master/module switches, tabs, date/range controls, direction and loading; JS owns UI state. CSS does not calculate price, Orders or verdicts. Property-level and screenshot audits were not performed.
