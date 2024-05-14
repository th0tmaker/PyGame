# Bomberman/timer_utils.py

def adjust_bomb_timer(start_time, duration, init_timer, on_expire_action):
    current_time = init_timer

    time_until_completion = (start_time + duration) - current_time

    if time_until_completion <= 0 and on_expire_action is not None:
        on_expire_action()

    return time_until_completion


def adjust_ice_tile_remove_timer(timers_dict, init_timer, duration, start_time, new_duration=None, new_start_time=None,
                                 on_expire_action=None):
    current_time = init_timer

    if new_duration is not None:
        start_time = new_start_time or current_time
        duration = new_duration

    elapsed_time = current_time - start_time
    remaining_time_at_pause = duration - elapsed_time
    timers_dict['remaining_time_at_pause'] = remaining_time_at_pause

    if remaining_time_at_pause <= 0 and on_expire_action is not None:
        on_expire_action()


def adjust_ice_tile_spawn_timer(start_time, duration, init_timer, on_expire_action):
    current_time = init_timer

    if current_time - start_time >= duration and on_expire_action is not None:
        on_expire_action()

        start_time = current_time

    return start_time


def update_start_time(timer_dict, current_time, paused_time, start_time_key):
    timer_dict[start_time_key] += current_time - paused_time


def update_timer_data_on_pause(timers_dict, paused):
    if paused:
        timers_dict['new_duration'] = timers_dict['remaining_time_at_pause']


def update_timer_data_on_resume(timers_dict, init_timer, resumed):
    if resumed:
        timers_dict['new_start_time'] = init_timer
