import time
from operator import attrgetter

class Measure_block():
  instances = []

  def __init__(self, loop=5, V_top=1.0, V_base=0.0, top_time=10.0, base_time=10.0, interval=10.0):
    self.set(len(Measure_block.instances), loop, V_top, V_base, top_time, base_time, interval)
    # Block_label(self)
    Measure_block.instances.append(self)

  @classmethod
  def reset_index(cls):
    for index, instance in enumerate(cls.instances):
      instance.index = index

  @classmethod
  def reset_selected(cls):
    for instance in cls.instances:
      instance.selected = False

  def set(self, index, loop, V_top, V_base, top_time, base_time, interval):
    self.index = index
    self.params = {
      "V_top" : V_top,
      "top_time" : top_time,
      "V_bot" : V_base,
      "bot_time" : base_time,
      "loop" : loop,
      "interval" : interval
    }
    # self.loop = loop
    # self.V_top = V_top
    # self.V_base = V_base
    # self.top_time = top_time
    # self.bottom_time = base_time
    # self.interval = interval
    self.expect_time = (self.params["bot_time"] + self.params["top_time"]) * self.params["loop"] + self.params["interval"]
    self.selected = False

  def measure(self, V_set, measure_times, dev, datas):
    self.stop_flag = False
    for _ in range(measure_times):
        if self.stop_flag == True:
            break
        
        dev.write(f"SOV{V_set}")
        dev.write("*TRG")
        datas.time_list.append(time.perf_counter())
        
        A=dev.query("N?")
        A_=float(A[3:-2])
        datas.A_list.append(A_)
        
        V=dev.query("SOV?")
        V_=float(V[3:-2])
        datas.V_list.append(V_)

  def run(self, dev, datas):
    for _ in range(int(self.params["loop"])):
      self.measure(self.params["V_bot"], self.params["bot_time"], dev, datas)
      self.measure(self.params["V_top"], self.params["top_time"], dev, datas)

    self.measure(self.params["V_bot"], self.params["interval"], dev, datas)

  def select(self, spinbox_instances):
    Measure_block.reset_selected()
    for instance, (key, value) in zip(spinbox_instances, self.params.items()):
      instance.insert(0, value)
    self.selected = True

  def delete(self):
    del self
    Measure_block.reset_index()

class Cycle():
  instances = []

  def __init__(self, loop=2):
    self.index = len(Cycle.instances)
    self.cycle_contents = []
    self.expect_time = 0.0
    self.loop = loop

  @classmethod
  def sort(cls):
    Cycle.instances.sort(key=attrgetter('cycle_contents[0].index'))

  def set(self, content):
    self.cycle_contents.append(content)
    self.expect_time = self.expect_time + content.expect_time
    self.cycle_contents.sort(key=attrgetter('index'))

  def remove(self, content_index):
    return self.cycle_contents.pop(content_index)

  def run(self, dev, datas):
    for _ in range(int(self.loop)):
      for block in self.cycle_contents:
        block.run(dev, datas)

class Measure_frame():
  def __init__(self):
    self.blocks = Measure_block.instances
    self.cycles = Cycle.instances

  def cluc_tot_time(self):
    self.expect_time = 0.0
    for instance in self.blocks:
      self.expect_time = self.expect_time + instance.expect_time

    for instance in self.cycles:
      self.expect_time = self.expect_time + instance.expect_time

  def make_block(self):
    Measure_block()
    self.blocks = Measure_block.instances

  def del_block(self, content):
    content.delete()

  def make_cycle(self):
    Cycle()

  def add_block_to_cycle(self, content):
    Cycle.set(content)
    self.blocks.pop(content)

  def remove_cycle_content(self, index):
    popped = Cycle.remove(index)
    self.blocks.append(popped)

  def run(self, dev, datas):
    self.measure_list = self.blocks
    count = 0
    for cycle in self.cycles:
      self.measure_list.insert(cycle[0].index - count, cycle)
      count = count + len(cycle) - 1
    
    for measure in self.measure_list:
      measure.run(dev, datas)