#! /usr/bin/env python3
import sys
import os
import re
import argparse
from collections import OrderedDict

# common

MAX_SIZE_TEMPLATE = '''\
#ParaverCFG
ConfigFile.Version: 3.4
ConfigFile.NumWindows: 2


################################################################################
< NEW DISPLAYING WINDOW Allocated site >
################################################################################
window_name Allocated site
window_type single
window_id 1
window_position_x 971
window_position_y 607
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 39.000000000000
window_minimum_y 2.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_filter_module evt_type 1 32000009
window_filter_module evt_type_label 1 "Allocation memory object"

################################################################################
< NEW DISPLAYING WINDOW Allocated data size >
################################################################################
window_name Allocated data size
window_type single
window_id 2
window_position_x 971
window_position_y 465
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 242970624.000000000000
window_minimum_y 1507.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode 1
window_drawmode_rows 1
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_filter_module evt_type 1 40000041

< NEW ANALYZER2D >
Analyzer2D.Name: Histogram: Allocation site / maximum allocation size
Analyzer2D.X: 1198
Analyzer2D.Y: 201
Analyzer2D.Width: 600
Analyzer2D.Height: 300
Analyzer2D.ControlWindow: 1
Analyzer2D.DataWindow: 2
Analyzer2D.Accumulator: Semantic
Analyzer2D.Statistic: Maximum
Analyzer2D.CalculateAll: True
Analyzer2D.HideCols: False
Analyzer2D.HorizVert: Horizontal
Analyzer2D.Color: True
Analyzer2D.SemanticColor: False
Analyzer2D.Zoom: Enabled
Analyzer2D.SortCols: False
Analyzer2D.SortCriteria: Average
Analyzer2D.Parameters: 4 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000
Analyzer2D.AnalysisLimits: Alltrace
Analyzer2D.ComputeYScale: False
Analyzer2D.Minimum: 2.000000000000
Analyzer2D.Maximum: @MAX_OBJECTS@
Analyzer2D.Delta: 1.000000000000
Analyzer2D.ComputeGradient: True
Analyzer2D.MinimumGradient: 1507.000000000000
Analyzer2D.MaximumGradient: 242970624.000000000000
Analyzer2D.PixelSize: 1
Analyzer2D.CodeColor: False
Analyzer2D.ShowOnlyTotals: False
Analyzer2D.ShortHeaderLabels: False

'''

# loads only

LD_LOAD_MISS_TEMPLATE = '''\
#ParaverCFG
ConfigFile.Version: 3.4
ConfigFile.NumWindows: 5


################################################################################
< NEW DISPLAYING WINDOW PEBS data referenced object.c1 >
################################################################################
window_name PEBS data referenced object.c1
window_type single
window_id 1
window_position_x 608
window_position_y 231
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 111.000000000000
window_minimum_y 2.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_filter_module evt_type 1 32000007
window_filter_module evt_type_label 1 "Memory object referenced by sampled address"
window_synchronize 1

################################################################################
< NEW DISPLAYING WINDOW PEBS loads not stores.c2.c1 >
################################################################################
window_name PEBS loads not stores.c2.c1
window_type single
window_id 2
window_position_x 490
window_position_y 136
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 1.000000000000
window_minimum_y 1.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Type}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Sign}, {topcompose2, As Is} } }
window_filter_module evt_type 1 32000000
window_filter_module evt_type_label 1 "Sampled address (load)"
window_synchronize 1

################################################################################
< NEW DISPLAYING WINDOW PEBS miss?.c1.c1 >
################################################################################
window_name PEBS miss?.c1.c1
window_type single
window_id 3
window_position_x 503
window_position_y 126
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 1.000000000000
window_minimum_y 1.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Is Equal (Sign)}, {topcompose2, As Is} } }
window_semantic_module topcompose1 Is Equal (Sign) { 1, { 1 2.000000000000 } }
window_filter_module evt_type 1 32000003
window_filter_module evt_type_label 1 "Memory hierarchy location for sampled address hit?"
window_synchronize 1

################################################################################
< NEW DISPLAYING WINDOW PEBS load miss.c1 >
################################################################################
window_name PEBS load miss.c1
window_type composed
window_id 4
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 2 3
window_position_x 629
window_position_y 252
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 1.000000000000
window_minimum_y 1.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 0.323696375130
window_end_time_relative 0.323696375130
window_object appl { 1, { All } }
window_begin_time_relative 0.320186982651
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }

################################################################################
< NEW DISPLAYING WINDOW Data object referened by PEBS load miss >
################################################################################
window_name Data object referened by PEBS load miss
window_type composed
window_id 5
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 1 4
window_position_x 677
window_position_y 361
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 111.000000000000
window_minimum_y 2.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_synchronize 1

< NEW ANALYZER2D >
Analyzer2D.Name: Histo: data-object referenced by PEBS load miss
Analyzer2D.X: 2621
Analyzer2D.Y: 257
Analyzer2D.Width: 600
Analyzer2D.Height: 300
Analyzer2D.ControlWindow: 5
Analyzer2D.DataWindow: 5
Analyzer2D.Accumulator: Semantic
Analyzer2D.Statistic: # Bursts
Analyzer2D.CalculateAll: True
Analyzer2D.HideCols: False
Analyzer2D.HorizVert: Horizontal
Analyzer2D.Color: True
Analyzer2D.SemanticColor: False
Analyzer2D.Zoom: Enabled
Analyzer2D.SortCols: False
Analyzer2D.SortCriteria: Average
Analyzer2D.Parameters: 4 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000
Analyzer2D.AnalysisLimits: Alltrace
Analyzer2D.ComputeYScale: False
Analyzer2D.Minimum: 2.000000000000
Analyzer2D.Maximum: @MAX_OBJECTS@
Analyzer2D.Delta: 1.000000000000
Analyzer2D.ComputeGradient: True
Analyzer2D.MinimumGradient: 1.000000000000
Analyzer2D.MaximumGradient: 5312.000000000000
Analyzer2D.DrawModeObjects: draw_maximum
Analyzer2D.DrawModeColumns: draw_maximum
Analyzer2D.PixelSize: 1
Analyzer2D.ColorMode: window_in_gradient_mode
Analyzer2D.ShowOnlyTotals: False
Analyzer2D.ShortHeaderLabels: False

'''

# loads + stores

LDST_LOAD_MISS_TEMPLATE = '''\
#ParaverCFG
ConfigFile.Version: 3.4
ConfigFile.NumWindows: 5


################################################################################
< NEW DISPLAYING WINDOW PEBS data referenced object.c1 >
################################################################################
window_name PEBS data referenced object.c1
window_type single
window_id 1
window_position_x 608
window_position_y 231
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 1284.000000000000
window_minimum_y 2.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_filter_module evt_type 1 32000007
window_filter_module evt_type_label 1 "Memory object referenced by sampled address"
window_synchronize 1

################################################################################
< NEW DISPLAYING WINDOW PEBS loads not stores.c2.c1 >
################################################################################
window_name PEBS loads not stores.c2.c1
window_type single
window_id 2
window_position_x 482
window_position_y 105
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 1.000000000000
window_minimum_y 1.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Type}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Is Equal (Sign)}, {topcompose2, As Is} } }
window_semantic_module topcompose1 Is Equal (Sign) { 1, { 1 32000000.000000000000 } }
window_filter_module evt_type 2 32000000 32000001
window_filter_module evt_type_label 2 "Sampled address (load)" "Sampled address (store)"
window_synchronize 1

################################################################################
< NEW DISPLAYING WINDOW PEBS miss?.c1.c1 >
################################################################################
window_name PEBS miss?.c1.c1
window_type single
window_id 3
window_position_x 503
window_position_y 126
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 1.000000000000
window_minimum_y 1.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Is Equal (Sign)}, {topcompose2, As Is} } }
window_semantic_module topcompose1 Is Equal (Sign) { 1, { 1 2.000000000000 } }
window_filter_module evt_type 1 32000003
window_filter_module evt_type_label 1 "Memory hierarchy location for sampled address hit?"
window_synchronize 1

################################################################################
< NEW DISPLAYING WINDOW PEBS load miss.c1 >
################################################################################
window_name PEBS load miss.c1
window_type composed
window_id 4
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 2 3
window_position_x 629
window_position_y 252
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 1.000000000000
window_minimum_y 1.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 0.323696375130
window_end_time_relative 0.323696375130
window_object appl { 1, { All } }
window_begin_time_relative 0.320186982651
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }

################################################################################
< NEW DISPLAYING WINDOW Data object referened by PEBS load miss >
################################################################################
window_name Data object referened by PEBS load miss
window_type composed
window_id 5
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 1 4
window_position_x 677
window_position_y 361
window_width 600
window_height 115
window_comm_lines_enabled false
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 84.000000000000
window_minimum_y 2.000000000000
window_compute_y_max true
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_synchronize 1

< NEW ANALYZER2D >
Analyzer2D.Name: Histo: data-object referenced by PEBS load miss
Analyzer2D.X: 742
Analyzer2D.Y: 367
Analyzer2D.Width: 600
Analyzer2D.Height: 300
Analyzer2D.ControlWindow: 5
Analyzer2D.DataWindow: 5
Analyzer2D.Accumulator: Semantic
Analyzer2D.Statistic: # Bursts
Analyzer2D.CalculateAll: True
Analyzer2D.HideCols: False
Analyzer2D.HorizVert: Horizontal
Analyzer2D.Color: True
Analyzer2D.SemanticColor: False
Analyzer2D.Zoom: Enabled
Analyzer2D.SortCols: False
Analyzer2D.SortCriteria: Average
Analyzer2D.Parameters: 4 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000
Analyzer2D.AnalysisLimits: Alltrace
Analyzer2D.ComputeYScale: False
Analyzer2D.Minimum: 2.000000000000
Analyzer2D.Maximum: @MAX_OBJECTS@
Analyzer2D.Delta: 1.000000000000
Analyzer2D.ComputeGradient: True
Analyzer2D.MinimumGradient: 1.000000000000
Analyzer2D.MaximumGradient: 367.000000000000
Analyzer2D.DrawModeObjects: draw_maximum
Analyzer2D.DrawModeColumns: draw_maximum
Analyzer2D.PixelSize: 1
Analyzer2D.ColorMode: window_in_gradient_mode
Analyzer2D.ShowOnlyTotals: False
Analyzer2D.ShortHeaderLabels: False

'''

LDST_L1D_STORE_MISS_TEMPLATE = '''\
#ParaverCFG
ConfigFile.Version: 3.4
ConfigFile.NumWindows: 5


################################################################################
< NEW DISPLAYING WINDOW Data-object referenced >
################################################################################
window_name Data-object referenced
window_type single
window_id 1
window_position_x 524
window_position_y 147
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_filter_module evt_type 1 32000007
window_filter_module evt_type_label 1 "Memory object referenced by sampled address"

################################################################################
< NEW DISPLAYING WINDOW MASK: is store sample >
################################################################################
window_name MASK: is store sample
window_type single
window_id 2
window_position_x 440
window_position_y 63
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Type}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Is Equal (Sign)}, {topcompose2, As Is} } }
window_semantic_module topcompose1 Is Equal (Sign) { 1, { 1 32000001.000000000000 } }
window_filter_module evt_type 2 32000000 32000001
window_filter_module evt_type_label 2 "Sampled address (load)" "Sampled address (store)"

################################################################################
< NEW DISPLAYING WINDOW MASK: is cache miss >
################################################################################
window_name MASK: is cache miss
window_type single
window_id 3
window_position_x 461
window_position_y 84
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 0.335715697596
window_end_time_relative 0.335715697596
window_object appl { 1, { All } }
window_begin_time_relative 0.316684525729
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Is Equal (Sign)}, {topcompose2, As Is} } }
window_semantic_module topcompose1 Is Equal (Sign) { 1, { 1 2.000000000000 } }
window_filter_module evt_type 1 32000003
window_filter_module evt_type_label 1 "Memory hierarchy location for sampled address hit?"

################################################################################
< NEW DISPLAYING WINDOW MASK: is store miss sample >
################################################################################
window_name MASK: is store miss sample
window_type composed
window_id 4
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 2 3
window_position_x 545
window_position_y 168
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }

################################################################################
< NEW DISPLAYING WINDOW Data-object referenced by store miss sample >
################################################################################
window_name Data-object referenced by store miss sample
window_type composed
window_id 5
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 1 4
window_position_x 2546
window_position_y 521
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 0.342890532616
window_end_time_relative 0.342890532616
window_object appl { 1, { All } }
window_begin_time_relative 0.292240150640
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }

< NEW ANALYZER2D >
Analyzer2D.Name: HISTO: Referenced data objects store miss L1D
Analyzer2D.X: 2619
Analyzer2D.Y: 445
Analyzer2D.Width: 600
Analyzer2D.Height: 300
Analyzer2D.ControlWindow: 5
Analyzer2D.DataWindow: 5
Analyzer2D.Accumulator: Semantic
Analyzer2D.Statistic: # Bursts
Analyzer2D.CalculateAll: True
Analyzer2D.HideCols: False
Analyzer2D.HorizVert: Horizontal
Analyzer2D.Color: True
Analyzer2D.SemanticColor: False
Analyzer2D.Zoom: Enabled
Analyzer2D.SortCols: False
Analyzer2D.SortCriteria: Average
Analyzer2D.Parameters: 4 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000
Analyzer2D.AnalysisLimits: Alltrace
Analyzer2D.ComputeYScale: False
Analyzer2D.Minimum: 2.000000000000
Analyzer2D.Maximum: @MAX_OBJECTS@
Analyzer2D.Delta: 1.000000000000
Analyzer2D.ComputeGradient: True
Analyzer2D.MinimumGradient: 1.000000000000
Analyzer2D.MaximumGradient: 171.000000000000
Analyzer2D.DrawModeObjects: draw_maximum
Analyzer2D.DrawModeColumns: draw_maximum
Analyzer2D.PixelSize: 1
Analyzer2D.ColorMode: window_in_gradient_mode
Analyzer2D.ShowOnlyTotals: False
Analyzer2D.ShortHeaderLabels: False

'''

LDST_L3_STORE_MISS_TEMPLATE = '''\
#ParaverCFG
ConfigFile.Version: 3.4
ConfigFile.NumWindows: 8


################################################################################
< NEW DISPLAYING WINDOW Data-object referenced >
################################################################################
window_name Data-object referenced
window_type single
window_id 1
window_position_x 524
window_position_y 147
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_filter_module evt_type 1 32000007
window_filter_module evt_type_label 1 "Memory object referenced by sampled address"

################################################################################
< NEW DISPLAYING WINDOW MASK: is store sample >
################################################################################
window_name MASK: is store sample
window_type single
window_id 2
window_position_x 440
window_position_y 63
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Type}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Is Equal (Sign)}, {topcompose2, As Is} } }
window_semantic_module topcompose1 Is Equal (Sign) { 1, { 1 32000001.000000000000 } }
window_filter_module evt_type 2 32000000 32000001
window_filter_module evt_type_label 2 "Sampled address (load)" "Sampled address (store)"

################################################################################
< NEW DISPLAYING WINDOW MASK: is cache miss >
################################################################################
window_name MASK: is cache miss
window_type single
window_id 3
window_position_x 461
window_position_y 84
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 0.335715697596
window_end_time_relative 0.335715697596
window_object appl { 1, { All } }
window_begin_time_relative 0.316684525729
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Last Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, Is Equal (Sign)}, {topcompose2, As Is} } }
window_semantic_module topcompose1 Is Equal (Sign) { 1, { 1 2.000000000000 } }
window_filter_module evt_type 1 32000003
window_filter_module evt_type_label 1 "Memory hierarchy location for sampled address hit?"

################################################################################
< NEW DISPLAYING WINDOW MASK: is store miss sample >
################################################################################
window_name MASK: is store miss sample
window_type composed
window_id 4
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 2 3
window_position_x 545
window_position_y 168
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }

################################################################################
< NEW DISPLAYING WINDOW Data-object referenced by store miss sample >
################################################################################
window_name Data-object referenced by store miss sample
window_type composed
window_id 5
window_factors 1.000000000000 1.000000000000
window_operation product
window_identifiers 1 4
window_position_x 2546
window_position_y 521
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_units Nanoseconds
window_maximum_y 18.000000000000
window_minimum_y 0.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 0.342890532616
window_end_time_relative 0.342890532616
window_object appl { 1, { All } }
window_begin_time_relative 0.292240150640
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }

################################################################################
< NEW DISPLAYING WINDOW L3 store misses / ns >
################################################################################
window_name L3 store misses / ns
window_type single
window_id 6
window_position_x 2436
window_position_y 412
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_color_mode window_in_null_gradient_mode
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 0.012321408783
window_minimum_y 0.000000097048
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Avg Next Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_semantic_module thread Avg Next Evt Val { 1, { 1 1.000000000000 } }
window_filter_module evt_type 1 11222333
window_filter_module evt_type_label 1 "Unknown"

################################################################################
< NEW DISPLAYING WINDOW Instructions / ns >
################################################################################
window_name Instructions / ns
window_type single
window_id 7
window_position_x 440
window_position_y 63
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_color_mode window_in_null_gradient_mode
window_logical_filtered true
window_physical_filtered false
window_comm_fromto true
window_comm_tagsize true
window_comm_typeval true
window_units Nanoseconds
window_maximum_y 7.852793372116
window_minimum_y 0.094426410030
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 14, { {cpu, Active Thd}, {appl, Adding}, {task, Adding}, {thread, Avg Next Evt Val}, {node, Adding}, {system, Adding}, {workload, Adding}, {from_obj, All}, {to_obj, All}, {tag_msg, All}, {size_msg, All}, {bw_msg, All}, {evt_type, =}, {evt_value, All} } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, As Is} } }
window_semantic_module thread Avg Next Evt Val { 1, { 1 1.000000000000 } }
window_filter_module evt_type 1 42000050
window_filter_module evt_type_label 1 "PAPI_TOT_INS [Instr completed]"

################################################################################
< NEW DISPLAYING WINDOW MASK: Low/High L3 store misses / Instruction >
################################################################################
window_name MASK: Low/High L3 store misses / Instruction
window_type composed
window_id 8
window_factors 1.000000000000 1.000000000000
window_operation divide
window_identifiers 6 7
window_position_x 2551
window_position_y 369
window_width 600
window_height 115
window_comm_lines_enabled true
window_flags_enabled false
window_noncolor_mode true
window_color_mode window_in_null_gradient_mode
window_units Nanoseconds
window_maximum_y 1.000000000000
window_minimum_y 1.000000000000
window_compute_y_max false
window_level thread
window_scale_relative 1.000000000000
window_end_time_relative 1.000000000000
window_object appl { 1, { All } }
window_begin_time_relative 0.000000000000
window_open false
window_drawmode draw_maximum
window_drawmode_rows draw_maximum
window_pixel_size 1
window_labels_to_draw 1
window_selected_functions { 5, { {appl, Adding}, {task, Adding}, {node, Adding}, {system, Adding}, {workload, Adding}, } }
window_compose_functions { 9, { {compose_cpu, As Is}, {compose_appl, As Is}, {compose_task, As Is}, {compose_thread, As Is}, {compose_node, As Is}, {compose_system, As Is}, {compose_workload, As Is}, {topcompose1, As Is}, {topcompose2, Is In Range} } }
window_semantic_module topcompose2 Is In Range { 2, { 1 1.000000000000, 1 0.001000000000 } }

< NEW ANALYZER2D >
Analyzer2D.Name: 3DH: Data-object referenced by store miss when in low/high L3 store misses ratio
Analyzer2D.X: 2559
Analyzer2D.Y: 555
Analyzer2D.Width: 600
Analyzer2D.Height: 300
Analyzer2D.ControlWindow: 5
Analyzer2D.DataWindow: 5
Analyzer2D.Accumulator: Semantic
Analyzer2D.Statistic: # Bursts
Analyzer2D.CalculateAll: True
Analyzer2D.HideCols: False
Analyzer2D.HorizVert: Horizontal
Analyzer2D.Color: True
Analyzer2D.SemanticColor: False
Analyzer2D.Zoom: Enabled
Analyzer2D.SortCols: False
Analyzer2D.SortCriteria: Average
Analyzer2D.Parameters: 4 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 -179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000000000
Analyzer2D.AnalysisLimits: Alltrace
Analyzer2D.ComputeYScale: False
Analyzer2D.Minimum: 2.000000000000
Analyzer2D.Maximum: @MAX_OBJECTS@
Analyzer2D.Delta: 1.000000000000
Analyzer2D.ComputeGradient: True
Analyzer2D.MinimumGradient: 2.000000000000
Analyzer2D.MaximumGradient: 35.000000000000
Analyzer2D.DrawModeObjects: draw_maximum
Analyzer2D.DrawModeColumns: draw_maximum
Analyzer2D.PixelSize: 1
Analyzer2D.ColorMode: window_in_gradient_mode
Analyzer2D.ShowOnlyTotals: False
Analyzer2D.ShortHeaderLabels: False
Analyzer2D.3D_ControlWindow: 8
Analyzer3D.ComputeYScale: False
Analyzer2D.3D_Minimum: 0.000000000000
Analyzer2D.3D_Maximum: 1.000000000000
Analyzer2D.3D_Delta: 1.000000000000
Analyzer2D.3D_FixedValue: 1.000000000000

'''


CONFIGS = {
    'ld': {
        'max-size': MAX_SIZE_TEMPLATE,
        'load-miss': LD_LOAD_MISS_TEMPLATE,
    },
    'ldst': {
        'max-size':     MAX_SIZE_TEMPLATE,
        'load-miss':      LDST_LOAD_MISS_TEMPLATE,
        'l1d-store-miss': LDST_L1D_STORE_MISS_TEMPLATE,
        'l3-store-miss':  LDST_L3_STORE_MISS_TEMPLATE,
    },
}


def matches(regex, text, data):
    m = re.match(regex, text)
    if m is not None:
        data.update(m.groupdict())
        return True
    else:
        return False

def parse_pcf(fname):
    '''
    <event type id>:
        gradient_id:
        id:
        label:
        values:
           <value id>:
                id:
                label:
    '''
    events = OrderedDict()
    values = None
    state = None
    with open(fname) as fin:
        for l in fin:
            l = l.rstrip()
            l = l.split('#')[0] # remove comments
            if l == '':
                continue

            if l == 'EVENT_TYPE':
                values = OrderedDict()
                state = 'events'
            elif l == 'VALUES':
                assert state == 'events'
                state = 'values'
            else:
                if state == 'events':
                    d = {}
                    if matches(r'(?P<gradient_id>\d+)\s+(?P<id>\d+)\s+(?P<label>.*)$', l, d):
                        for k in ('id', 'gradient_id'):
                            d[k] = int(d[k])
                        d['values'] = values
                        events[d['id']] = d
                elif state == 'values':
                    d = {}
                    if matches(r'(?P<id>\d+)\s+(?P<label>.*)$', l, d):
                        for k in ('id', ):
                            d[k] = int(d[k])
                        values[d['id']] = d
    return events


OBJECTS_EVENT = 32000009 

def gen_configs(pcf_fname, outdir, group):
    pcf = parse_pcf(pcf_fname)
    if OBJECTS_EVENT not in pcf:
        return None
    max_obj = max(pcf[OBJECTS_EVENT]['values'].keys())
    print("INFO Max object ID in '{}' is {}".format(pcf_fname, max_obj), file=sys.stderr)

    out_files = {}
    for name,tpl in CONFIGS[group].items():
        fname = os.path.join(outdir, '{}_{}.cfg'.format(group, name))

        contents, num_replacements = re.subn(r'@MAX_OBJECTS@', str(max_obj), tpl)
        if num_replacements == 0:
            print("WARN No substitution of MAX_OBJECTS var for '{}'".format(fname), file=sys.stderr)

        assert fname not in out_files
        out_files[fname] = contents

    return out_files


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ld', help='the pcf file of the loads trace')
    p.add_argument('--ldst', help='the pcf file of the loads+stores trace')
    p.add_argument('outdir', help='output directory')
    p.add_argument('-f', '--force', help='override already existing output files', action='store_true')
#    p.add_argument('-a', '--all-or-none', help='do not generate any file if any of then cannot be generated', action='store_true')
    args = p.parse_args()

    if args.ld is None and args.ldst is None:
        print("ERROR Specify the *.pcf input file(s) with --ld and/or --ldst flags", file=sys.stderr)
        return 1

    if os.path.exists(args.outdir) and not os.path.isdir(args.outdir):
        print("ERROR Output dir '{}' is not a directory".format(args.outdir), file=sys.stderr)
        return 1


    all_out_files = {}
    if args.ld is not None:
        if not os.path.isfile(args.ld):
            print("ERROR The --ld file '{}' doesn't exist or is not a file".format(args.ld), file=sys.stderr)
            return 1
        out_files = gen_configs(args.ld, args.outdir, 'ld')
        if out_files is None:
            print("ERROR Couldn't parse pcf file '{}'".format(args.ld), file=sys.stderr)
            return 1
        assert all(fname not in all_out_files for fname in out_files.keys())
        all_out_files.update(out_files)    


    if args.ldst is not None:
        if not os.path.isfile(args.ldst):
            print("ERROR The --ldst file '{}' doesn't exist or is not a file".format(args.ldst), file=sys.stderr)
            return 1
        out_files = gen_configs(args.ldst, args.outdir, 'ldst')
        if out_files is None:
            print("ERROR Couldn't parse pcf file '{}'".format(args.ldst), file=sys.stderr)
            return 1
        assert all(fname not in all_out_files for fname in out_files.keys())
        all_out_files.update(out_files)    
            

    if not os.path.exists(args.outdir):
        os.makedirs(os.path.abspath(args.outdir))
#    else:
#        if not args.force:
#            # check if any output file already exists
#            is_error=False
#            for f in all_out_files.keys():
#                if os.path.exists(f):
#                    print("ERROR output file '{}' already exists".format(f), file=sys.stderr)
#                    is_error = True
#            if is_error:
#                print("No output files were generated", file=sys.stderr)
#                return 1
    ret = 0
    for fname,contents in all_out_files.items():
        if not args.force and os.path.exists(fname):
            print("ERROR Output file '{}' already exists".format(fname), file=sys.stderr)
            ret = 2
            continue

        print("INFO Writing file '{}'".format(fname), file=sys.stderr)
        with open(fname, 'w') as fout:
            fout.write(contents)
    
    return ret


if __name__ == '__main__':
    sys.exit(main())
    



