from threading import Thread

from src.gui.widgets import TabNarma, Statusbar
from src.core import narma_run
from src.core.measurement import CommonParameters
from src.core.measurement import NarmaParam
from src.utils import timer

from _interface import ExecutionStrategy

class NarmaExecutionStrategy(ExecutionStrategy):
    def __init__(self, tab_instance: TabNarma, status_bar: Statusbar):
        self.tab = tab_instance
        self.status_bar = status_bar

    def get_parameters(self) -> NarmaParam:
        # measure_type_index = fetch_measure_type_index("NARMA")        
        return NarmaParam(
            use_database=self.tab.is_use_prepared_array,
            model=self.tab.narma_model,
            pulse_width=self.tab.pulse_width,
            off_width=self.tab.off_width,
            tick=self.tab.tick,
            nodes=self.tab.nodes,
            discrete_time=self.tab.discrete_time,
            bot_voltage=self.tab.bot_voltage,
            top_voltage=self.tab.top_voltage,
            base_voltage=self.tab.base_voltage
        )
    
    def pre_execute(self) -> None:
        tot_time = (self.tab.pulse_width + self.tab.off_width) * self.tab.discrete_time
        timer_thread = Thread(target=timer, args=(tot_time, self.status_bar))
        timer_thread.start()

    def execute(self, parameters: NarmaParam, common_param: CommonParameters) -> None:
        def target(parameters, common_param):
            try:
                narma_run(parameters, common_param)
            except Exception as e:
                print(f"Error in NARMA execution: {e}")
        
        thread = Thread(target=target, args=(parameters, common_param))
        thread.start()
