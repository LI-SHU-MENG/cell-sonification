import pandas as pd
import pretty_midi
import numpy as np

# 读取数据
df = pd.read_csv(
    "/Users/shumengli/Python_tuto/sonification_cell_test/cell table.csv")
data = df["AngleXY"].values

# MIDI音高范围归一化
min_pitch = 60
max_pitch = 127
normalized = np.interp(data, (min(data), max(data)), (min_pitch, max_pitch))

# 创建 PrettyMIDI 对象和乐器
midi = pretty_midi.PrettyMIDI()
instrument = pretty_midi.Instrument(program=0)  # 钢琴

start_time = 0
duration = 0.5  # 每个音符时长

# Pitch Bend 范围，通常合成器设置12半音（±8192），这里先设定
pitch_bend_range = 12  # 半音


def pitch_to_pitchbend(current_pitch, target_pitch, pitch_bend_range=12, steps=10):
    """
    根据当前音高和目标音高，生成Pitch Bend值列表，实现滑音。
    Pitch Bend值范围是-8192到8191
    """
    semitone_diff = target_pitch - current_pitch
    # 计算所需pitch bend值（线性映射）
    pitch_bend_max = 8191
    pitch_bend_min = -8192

    # 根据音高差和pitch bend范围，计算pitch bend的目标值
    # 例如pitch_bend_range=12表示±12半音对应±8192
    target_bend_value = int(
        (semitone_diff / pitch_bend_range) * pitch_bend_max)
    target_bend_value = max(
        min(target_bend_value, pitch_bend_max), pitch_bend_min)

    # 从0平滑过渡到target_bend_value
    return np.linspace(0, target_bend_value, steps).astype(int)


previous_pitch = normalized[0]

for i, pitch in enumerate(normalized):
    pitch = int(pitch)

    # 添加滑音Pitch Bend事件（如果不是第一个音符）
    if i > 0:
        steps = 10
        bends = pitch_to_pitchbend(
            previous_pitch, pitch, pitch_bend_range=pitch_bend_range, steps=steps)
        # 分布在音符开始前的一小段时间内插入pitch bend事件
        bend_start = start_time - 0.1  # 提前0.1秒开始滑音
        for step_i, bend_value in enumerate(bends):
            bend_time = bend_start + (step_i / steps) * 0.1  # 0.1秒内完成滑音
            pb = pretty_midi.PitchBend(pitch=bend_value, time=bend_time)
            instrument.pitch_bends.append(pb)

    # 添加音符事件
    note = pretty_midi.Note(
        velocity=100,
        pitch=pitch,
        start=start_time,
        end=start_time + duration
    )
    instrument.notes.append(note)

    previous_pitch = pitch
    start_time += duration

midi.instruments.append(instrument)
midi.write("sonified_output_with_glide.mid")
