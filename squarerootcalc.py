import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.text import Text
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from matplotlib.table import Table
import numpy as np

   
class solution_zone:
    def draw_handler(self, evt):
        self.fig.canvas.mpl_disconnect(self.draw_ref)
       
        # Getting the bottom right cell(the new coordinates of the axes)
        cell_keys=self.tab.get_celld()
        max_row_num=max(k[0] for k in cell_keys)
        max_col_num=max(k[1] for k in cell_keys)
        cell_xy=self.tab[max_row_num, max_col_num].xy
        cell_width=self.tab[max_row_num, max_col_num].get_width()
        cell_height=self.tab[max_row_num, max_col_num].get_height()
        # Getting the axes size in inches. 
        x0_in_inches=self.figure_size[0]*self.axes_pos.x0
        y0_in_inches=self.figure_size[1]*self.axes_pos.y0
        x1_in_inches=self.figure_size[0]*self.axes_pos.x1
        y1_in_inches=self.figure_size[1]*self.axes_pos.y1
        width_in_inches=x1_in_inches-x0_in_inches
        height_in_inches=y1_in_inches-y0_in_inches

        y0=cell_xy[1]
        x1=cell_xy[0]+cell_width

        # Scaling the table
        scale_x=1/x1
        scale_y=1/(1-y0)
        self.tab.scale(scale_x,scale_y)
        self.ax.set_ylim(y0,1)
        self.ax.set_xlim(0,x1)
        
        # New axes size in inchecs
        new_axes_width_in_inches = width_in_inches*x1
        new_axes_height_in_inches = height_in_inches*(1-y0)
        
        new_figure_width = 0.4+new_axes_width_in_inches
        new_figure_height = 0.4+new_axes_height_in_inches
        
        relative_x0=0.2/new_figure_width
        relative_y0=0.2/new_figure_height
        relative_width=new_axes_width_in_inches/new_figure_width
        relative_height=new_axes_height_in_inches/new_figure_height

        
        self.ax.set_position([relative_x0,
                              relative_y0,
                              relative_width, 
                              relative_height])
        self.fig.set_size_inches(new_figure_width, new_figure_height)
        self.fig.canvas.draw()
     
        
    def print_in_row(self,text, row_num, col_num,edges):
        cur_col_num=col_num
        for strindex_to in range(len(text),0,-2):
            strindex_from=strindex_to-2
            if strindex_from<0:
                strindex_from=0
            cell_text=text[strindex_from:strindex_to]
            if cur_col_num == self.dec_point_col:
                cell_text+='.'
            cell=self.tab.add_cell(row_num,cur_col_num,width=0.1,height=0.025,
                                   text=cell_text,loc='right')
            cell.visible_edges=edges
            cell.PAD = 0.25 if cur_col_num==1 else 0.2
            cur_col_num-=1
            
    def create_sidebar_str(self,sidebar_value,col_num):
        sidebar_str=str(sidebar_value)
        if self.dec_point_col==-1:
            return sidebar_str
        if col_num<self.dec_point_col:
            return sidebar_str
        if col_num==self.dec_point_col:
            return sidebar_str+'.'
        after_point_digits=col_num-self.dec_point_col
        sidebar_orig_len=len(sidebar_str)
        if sidebar_orig_len<after_point_digits:
            ret_value='0.' + '0'*(after_point_digits-sidebar_orig_len+1)+\
                      sidebar_str
        else:
            if sidebar_orig_len==after_point_digits:
                before_point='0'
            else:
                before_point=sidebar_str[:sidebar_orig_len-after_point_digits]
            ret_value=before_point+'.'+sidebar_str[-after_point_digits:]
        return ret_value
        
    
    def long_division(self):
        operand_len = len(self.operand_str)
        strindex_from=0
        # Will the first cell contain one digits or 2?
        strindex_to=1 if operand_len&1 else 2
            
        result=0
        col_num=1
        row_num=2
        remainder_str=''
        self.tab.auto_set_column_width(0)

        while strindex_to <= operand_len:
            remainder_str+=self.operand_str[strindex_from:strindex_to]
            remainder=int(remainder_str)
            if(row_num>2):
                self.print_in_row(remainder_str,row_num,col_num,'')
                row_num+=1
            twenty_result=20*result
            # find next digit
            for next_digit in range(9,-1,-1):
                sidebar_value=twenty_result + next_digit
                prod=sidebar_value*next_digit
                if prod<=remainder:
                    break
            sidebar_str=self.create_sidebar_str(sidebar_value,col_num)
            cell=self.tab.add_cell(row_num,0,width=0.1,height=0.02,
                                   text=sidebar_str,loc='right')
            cell.visible_edges='R'
            #cell.PAD=0.1
            result=result*10+next_digit
            digit_str=str(next_digit)
            if col_num==self.dec_point_col:
                digit_str+='.'
            digit_str='${'+digit_str+'}$'
            cell=self.tab.add_cell(0,col_num,width=0.1,height=0.025,text=digit_str,
                                   loc='right')
            cell.visible_edges=''
            cell.PAD=0.25 if col_num==1 else 0.2
            self.print_in_row(str(prod),row_num,col_num,'B')
            row_num+=1

            remainder -= prod
            if not remainder:
                remainder_str=''
            else:
                remainder_str=str(remainder)
            col_num+=1
            strindex_from=strindex_to
            strindex_to+=2
            
    def print_radical_line(self):
        if (self.after_point==''):
            self.dec_point_col=-1
        else:
            dec_point_index=len(self.before_point)
            self.dec_point_col=int((dec_point_index + (dec_point_index&1))/2)
		# Print the first digit or two digits
        if 	len(self.operand_str)&1:
            cell_value=self.operand_str[0]
            strindex=1
        else:
            cell_value=self.operand_str[0:2]
            strindex=2
        if(self.dec_point_col==1):
            cell_value+='.'
        self.tab.auto_set_column_width(1)
        cell=self.tab.add_cell(1,1,width=0.1,height=0.02,loc='right',
                               text='$\sqrt{'+cell_value+'}$')
        cell.visible_edges=''
        col_index=2
        for strindex in range(strindex,len(self.operand_str),2):
            cell_value=self.operand_str[strindex:strindex+2]
            if col_index==self.dec_point_col:
                cell_value+='.'
            self.tab.auto_set_column_width(col_index)
            cell=self.tab.add_cell(1,col_index,width=.1,height=0.02,loc='right',
                                   text='$\overline{'+cell_value+'}$')
            cell.visible_edges=''
            col_index+=1
		
    def __init__(self, numb, prec):
        gps=numb.pattern.search(numb.val).groups()
        self.before_point=gps[0]
        if not self.before_point:
            self.before_point='0'
        self.after_point=gps[3]
        if (self.after_point==None):
            self.after_point=''
        if (len(self.after_point)&1):
            self.after_point += '0'
        if (prec.val and 2*int(prec.val)>len(self.after_point)):
            self.after_point+='0'*(2*int(prec.val)-len(self.after_point))
        self.operand_str=self.before_point + self.after_point
        
        self.fig,self.ax=plt.subplots()

        self.ax.set_axis_off()
        self.fig.set_size_inches(10,10)
        self.axes_pos=self.ax.get_position()
        self.figure_size=self.fig.get_size_inches()
        self.tab=Table(self.ax,loc='upper left',in_layout=True)
        self.tab.AXESPAD=0

        self.print_radical_line()
        self.long_division()

        self.ax.add_table(self.tab)
        self.draw_ref=self.fig.canvas.mpl_connect('draw_event',self.draw_handler)

        plt.show()
import re
class numeric_field:
    def __init__(self, inp_ax, label, regexp, maxlen, decpoint=None):
        self.val=''
        self.curpos=0
        self.pattern=re.compile(regexp)
        self.maxlen=maxlen
        self.decpoint=decpoint
        self.tb=TextBox(inp_ax,label)
        self.tb.on_text_change(self.tc_func)

    def tc_func(self,inp):
        if (len(inp)>self.maxlen):
            self.tb.cursor_index=self.curpos
            self.tb.set_val(self.val)
            return
        if (self.decpoint and inp.find('.')<0 and len(inp)>self.maxlen-1):
            self.tb.cursor_index=self.curpos
            self.tb.set_val(self.val)
            return
        if (not self.pattern.match(inp)):
            self.tb.cursor_index=self.curpos
            self.tb.set_val(self.val)
            return
        self.val=inp
        self.curpos=self.tb.cursor_index


class input_zone:

    def click_func(self,evt):
        self.sz=solution_zone(self.num_tb,self.prec_tb)

    def __init__(self):
        self.fig,self.ax=plt.subplots(nrows=3)
        self.ax[0].set_position([0.2,0.85,0.7,0.1])
        self.num_tb = numeric_field(self.ax[0],'Enter Number','^(\d*)((\.)(\d*))?$',
                                    21,True)
        self.ax[1].set_position([0.2,0.74,0.7,0.1])
        self.prec_tb = numeric_field(self.ax[1],'Digits After Point','^(\d*)$',2)
        self.ax[2].set_position([0.2,0.6,0.1,0.1])
        self.submit=Button(self.ax[2],label="Submit")
        self.submit.on_clicked(self.click_func)
        plt.show()

        
input_zone();


