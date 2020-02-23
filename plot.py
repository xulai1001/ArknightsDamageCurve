#!/usr/bin/env python
# coding:utf-8

import csv
import os
import matplotlib.pyplot as plt
import matplotlib.image as image
from matplotlib.ticker import *
from matplotlib.offsetbox import *
from character import *
from pprint import pprint

# ========== Preset some params for Matplotlib ==========
# You may change fonts. Just follow instructions of Matplotlib
# https://www.zhihu.com/question/25404709 may help
# Remember to use "ttf" rather than "ttc" or "otf", otherwise it is impossible to generate "*.pdf" file
plt.rcParams["font.sans-serif"] = ["Source Han Sans SC"]
plt.rcParams["axes.unicode_minus"] = False
ExtraGiantFont = {"family": "Source Han Sans SC", "size": 20}
GiantFont = {"family": "Source Han Sans SC", "size": 16}
BigDescriptionFont = {"family": "Source Han Sans SC", "size": 12}
DescriptionFont = {"family": "Source Han Sans SC", "size": 9}
MediumSmallDescriptionFont = {"family": "Source Han Sans SC", "size": 7.5}
SmallDescriptionFont = {"family": "Source Han Sans SC", "size": 6}
TinyDescriptionFont = {"family": "Source Han Sans SC", "size": 5}
ExtraTinyDescriptionFont = {"family": "Source Han Sans SC", "size": 4}


def plot_enemy_info(figure, enemy):
    """
    Draw the image and show basic info of enemy target.

    :param figure:  <Figure> the figure to draw on
    :param enemy:   <str> name of enemy

    :return:    target_num:     <int> the number of target enemies
                target_hp:      <int> total HP of target enemies
                defense:        <int> defense of target enemies
                mr:             <int> magic resistance of target enemies
    """
    # Load data
    path = os.getcwd()
    hp = enemy_dict[enemy]["HP"]
    # Avoid slay line greater than 135,000 (which will be covered by legend, making it hard to recognize),
    # and also making it as big as possible, as too low slay line will result in too short slay time.
    if hp > 67500:
        target_num = 1
    elif hp > 27000:
        target_num = int(90000 / hp) + 1
    elif hp > 13500:
        target_num = 5
    else:
        target_num = 5 * int(18000 / hp) + 5
    target_hp = hp * target_num
    defense = enemy_dict[enemy]["def"]
    mr = enemy_dict[enemy]["MR"]
    img = image.imread(os.path.join(path, "enemy/", enemy_dict[enemy]["img"]))
    if enemy_dict[enemy].get("rank"):
        rank = image.imread(os.path.join(path, "enemy/", enemy_dict[enemy]["rank"]))
    else:
        rank = None
    if enemy_dict[enemy].get("tag"):
        tag = [image.imread(os.path.join(path, "enemy/", single_tag)) for single_tag in enemy_dict[enemy]["tag"]]
    else:
        tag = []

    # Draw images and show info
    newax = figure.add_axes([0.08, 0.46, 0.2, 0.2], anchor="SW", zorder=995)
    newax.axis('off')
    newax.set_xlim([0, 400])
    newax.set_ylim([0, 200])
    newax.imshow(img, extent=[0, 180, 0, 180], alpha=0.85, zorder=996)
    newax.text(195, 133, "生命: %-6d" % hp, fontdict=GiantFont)
    newax.text(195, 78, "防御: %-4d" % defense, fontdict=GiantFont)
    newax.text(195, 23, "法抗: %-2d" % mr, fontdict=GiantFont)
    newax.plot([270, 290], [90, 90], c="steelblue", alpha=0.2, lw=97)
    if rank is not None:
        newax.imshow(rank, extent=[110, 180, 0, 70], alpha=0.5, zorder=997)
    if tag:
        y_pos = -45
        for idx, t in enumerate(tag):
            y_pos += 45
            newax.imshow(t, extent=[0, 45, y_pos, y_pos + 45], alpha=0.9, zorder=998)

    return target_num, target_hp, defense, mr


def plot_curve(char_dict, stage, write_file, axes, pick_list, defense, mr,
               baseline=None, show_slay_line=False, target_hp=None):
    """
    Plot damage curves for characters in `pick_list`.

    :param char_dict:       <dict> the dictionary containing character info
    :param stage:           <int> stage of characters
    :param write_file:      <i/o> file to write

    :param axes:            <Axes> the axes to plot damage curves on
    :param pick_list:       <list> each element is a name of picked character
                                Details refer to `Overall parameters introduction`
    :param defense:         <int> defense of enemy
    :param mr:              <int> magic resistance of enemy
    :param baseline:        <str> name of baseline character
                                Details refer to `Overall parameters introduction`
    :param show_slay_line:  <bool> whether to show slay line or not
                                Details refer to `Overall parameters introduction`
    :param target_hp:       <int> HP of enemy target. Only effective when `show_slay_line` is True

    :return:    legend_list:    <list> info used in `plot_legend`
                slay_list:      <list> info used in `plot_slay_line`
    """
    legend_list, slay_list = list(), list()
    y_labels = []
    dps_list = []
    colors = []
    for desc, char in char_dict.items():
        # print(desc)
        # Filter characters
        _, name, skill = desc.split("-")

        if pick_list and ((name not in pick_list and "%s%s" % (name, skill[0]) not in pick_list) and
                          "%s-%s技能" % (name, skill[0]) != baseline):
            continue

        # Plot damage curve for each character
        damage_node = char.simulate(defense, mr)
        damage_record = "\t".join(["(%.3f, %.0f)" % (x[0], x[1]) for x in damage_node])
        dps = damage_node[-1][1] / damage_node[-1][0]
        dps_list.append(round(dps))


        #x_labels = [x[0] for x in damage_node]
        #y_labels = [x[1] for x in damage_node]

        desc = description_level_change(stage, char, desc)
        y_labels.append(desc)
        colors.append(color_dict[char.name])

       # axes.plot(x_labels, y_labels, label=desc, c=color_dict[char.name], alpha=0.8, ls=ls_dict[char.rarity],
       #           lw=lw_dict[char.skill_order], marker=mk_dict[char.rarity], ms=ms_dict[char.skill_order])
        # Write data
        write_file.write(desc + "\t" + damage_record + "\n")

        # Prepare data for legend
        legend_list.append([char, desc, damage_node[-1][1]])

    # sort    
    dps_list, colors, y_labels = zip(*sorted(zip(dps_list, colors, y_labels)))
    pprint(y_labels)
    pprint(dps_list)
    axes.barh(y_labels, dps_list, 
        color=colors, alpha=0.8)
    i = 0
    for x, y in zip(dps_list, y_labels):
        axes.text(dps_list[i] + 10, i - 0.05, dps_list[i])
        i+=1

    axes.set_xlim([0, dps_list[-1] * 1.1])

    return legend_list, slay_list


def plot_legend(axes, legend_list, damage_baseline=100000, ignore_polish=False, multi_target_label=False):
    """
    Plot legends w.r.t. legend list on given axes

    :param axes:            <Axes> the axes to plot legends on
    :param legend_list:     <list> each element is a list as [<char object>, char name, damage]
    :param damage_baseline: <int> the baseline damage
    :param ignore_polish:   <bool> all legends with damage lower than `polish_line` will be ignored
                                Details refer to `Overall parameters introduction`
    :param multi_target_label:  <bool> whether to add an extra legend showing how many targets one will hit per attack

    :return:    max_damage: <int> maximal damage among all characters
    """
    legend_list.sort(key=lambda x: x[2], reverse=True)
    max_damage = legend_list[0][2]

    # Ignore legends with damage lower than `polish_line`
    if ignore_polish:
        polish_line = int((max_damage / 10000) ** (1 / 2) * 10000)
        legend_list = [item for item in legend_list if (item[2] > polish_line or item[2] == damage_baseline)]
    else:
        polish_line = -1

    # Stagger the legends
    legend_list[0].append(legend_list[0][2])
    for i in range(1, len(legend_list)):
        if legend_list[i - 1][3] - legend_list[i][2] < max_damage / 40:
            legend_list[i].append(legend_list[i - 1][3] - max_damage / 40)
        else:
            legend_list[i].append(legend_list[i][2])

    # Plot the polish damage line
    if ignore_polish:
        if polish_line > damage_baseline:
            if legend_list[-2][3] - polish_line < max_damage / 40:
                polish_y_pos = legend_list[-2][3] - max_damage / 40
            else:
                polish_y_pos = polish_line
            if polish_line - legend_list[-1][3] < max_damage / 40:
                legend_list[-1][3] = polish_y_pos - max_damage / 40
        else:
            if legend_list[-1][3] - polish_line < max_damage / 40:
                polish_y_pos = legend_list[-1][3] - max_damage / 40
            else:
                polish_y_pos = polish_line

        if polish_line < 10 * damage_baseline:
            dmg_ratio = "%.0f%%" % (polish_line / damage_baseline * 100)
        elif polish_line < 100 * damage_baseline:
            dmg_ratio = "%.1fk%%" % (polish_line / damage_baseline / 10)
        elif polish_line < 1000 * damage_baseline:
            dmg_ratio = "%.0fk%%" % (polish_line / damage_baseline / 100)
        else:
            dmg_ratio = r"99k%+"

        axes.plot([0, 300], [0, polish_line], c="black", alpha=0.8, ls="-", lw=3)
        axes.plot([305, 325, 340, 345], [polish_line, polish_line, polish_y_pos, polish_y_pos],
                  c="black", alpha=0.8, ls="-", lw=2)
        axes.plot([348, 355.7], [polish_y_pos, polish_y_pos], c="black", alpha=0.3, ls="-", lw=9.3)
        axes.plot([360, 420], [polish_y_pos, polish_y_pos], c="black", alpha=0.1, ls="-", lw=9.3)
        axes.text(346.3, polish_y_pos - max_damage / 120, dmg_ratio, fontdict=DescriptionFont)
        axes.text(359, polish_y_pos - max_damage / 120, "抛光线", fontdict=DescriptionFont)
        axes.text(405, polish_y_pos - max_damage / 120, polish_line, fontdict=DescriptionFont)

    # Plot legends
    for char, name, dmg, text_y_pos in legend_list:
        dmg_value = "%.0f" % dmg
        if dmg < 10 * damage_baseline:
            dmg_ratio = "%.0f%%" % (dmg / damage_baseline * 100)
        elif dmg < 100 * damage_baseline:
            dmg_ratio = "%.1fk%%" % (dmg / damage_baseline / 10)
        elif dmg < 1000 * damage_baseline:
            dmg_ratio = "%.0fk%%" % (dmg / damage_baseline / 100)
        else:
            dmg_ratio = r"99k%+"

        axes.plot([305, 325, 340, 345], [dmg, dmg, text_y_pos, text_y_pos], c=color_dict[char.name],
                  alpha=0.8, ls=ls_assist_dict[char.rarity], lw=lw_dict[char.skill_order] / 1.5,
                  marker=mk_dict[char.rarity], ms=ms_dict[char.skill_order] / 1.5)
        axes.plot([348, 355.7], [text_y_pos, text_y_pos], c=color_dict[char.name], alpha=0.4, ls="-", lw=9.3)
        axes.plot([360, 420], [text_y_pos, text_y_pos], c=color_dict[char.name], alpha=0.15, ls="-", lw=9.3)
        axes.text(346.3, text_y_pos - max_damage / 120, dmg_ratio, fontdict=DescriptionFont)
        if len(name) <= 15:
            axes.text(359, text_y_pos - max_damage / 120, name, fontdict=DescriptionFont)
        elif len(name) <= 18:
            axes.text(359, text_y_pos - max_damage / 120, name, fontdict=MediumSmallDescriptionFont)
        else:
            axes.text(359, text_y_pos - max_damage / 120, name, fontdict=SmallDescriptionFont)
        axes.text(405, text_y_pos - max_damage / 120, dmg_value, fontdict=DescriptionFont)

        if multi_target_label:
            axes.plot([425.5, 452.5], [text_y_pos, text_y_pos], c=color_dict[char.name], alpha=0.2, ls="-", lw=8)
            desc = char.multi_target_desc
            if desc != "单体攻击":
                axes.text(424.7, text_y_pos - max_damage / 200, desc, fontdict=SmallDescriptionFont)
            else:
                axes.text(424.7, text_y_pos - max_damage / 200, desc, fontdict=SmallDescriptionFont, alpha=0.5)

    if multi_target_label:
        axes.plot([426.5, 450], [max_damage * 41 / 40, max_damage * 41 / 40], c="black", alpha=0.1, ls="-", lw=9.3)
        axes.text(426, max_damage * 611 / 600, "设定攻击目标数", fontdict=MediumSmallDescriptionFont)

    # Annotate damage baseline
    if damage_baseline is not None:
        axes.text(305, damage_baseline - max_damage / 120, "伤害基准线", fontdict=DescriptionFont)

    # Generate regular legend if the number of legend is not more than 30
    if len(legend_list) <= 30:
        axes.legend(loc=2, prop=BigDescriptionFont, ncol=3, labelspacing=0.3, borderpad=0.6, columnspacing=1,
                    markerscale=2, framealpha=0.7, facecolor="whitesmoke", edgecolor="gray")

    return max_damage


def plot_slay_line(axes, slay_list, target_num, enemy, target_hp, max_damage, show_slay_time_tag=True):
    """
    Plot slay line on given axes.

    :param axes:        <Axes> the axes to plot slay line on
    :param target_num:  <int> the number of target enemies
    :param enemy:       <str> the name of target enemies
    :param target_hp:   <int> total HP of target enemies
    :param slay_list:   <list> each element is a list as [<char object>, text description, time to slay the target]
    :param max_damage:  <int> maximal damage of all characters, which is used for positioning
    :param show_slay_time_tag:  <bool> whether to show slay time tag

    :return:            None
    """
    # Plot the slay line of given enemy
    slay_line_text = "斩杀线: %s个%s\n总HP: %-6d" % (target_num, enemy, target_hp)
    axes.plot([-5, 302], [target_hp, target_hp], label=None, c="black", alpha=0.75, ls="-", lw=2)
    if max_damage > 520000:
        axes.text(-3, target_hp + max_damage / 130, slay_line_text, fontdict=BigDescriptionFont,
                  horizontalalignment='left', verticalalignment='bottom')
        axes.plot([-5, -5, 30], [target_hp, target_hp + max_damage / 12, target_hp + max_damage / 12],
                  label=None, c="black", alpha=0.5, ls="-", lw=1)
    elif max_damage > 300000:
        axes.text(-3, target_hp - max_damage / 80, slay_line_text, fontdict=BigDescriptionFont,
                  horizontalalignment='left', verticalalignment='top')
        axes.plot([-5, -5, 30], [target_hp, target_hp - max_damage / 12, target_hp - max_damage / 12],
                  label=None, c="black", alpha=0.5, ls="-", lw=1)
    else:
        axes.text(-3, max_damage / 3 + max_damage / 100, slay_line_text, fontdict=BigDescriptionFont,
                  horizontalalignment='left', verticalalignment='bottom')
        axes.plot([-5, -5, 30], [target_hp, max_damage / 3, max_damage / 3],
                  label=None, c="black", alpha=0.5, ls="-", lw=1)

    slay_list.sort(key=lambda x: x[2], reverse=False)

    if show_slay_time_tag:
        # Stagger the slay time tags
        positioning_mat = np.zeros([325, 8])
        for i in range(0, len(slay_list)):
            anchor_x_pos = int(slay_list[i][2])
            y_idx_list = [(k, list(positioning_mat[anchor_x_pos - 25:anchor_x_pos, k]).count(True)) for k in range(8)]
            y_idx_list.sort(key=lambda x: (x[1], x[0]))
            anchor_y_idx = y_idx_list[0][0]
            positioning_mat[anchor_x_pos - 25:anchor_x_pos, anchor_y_idx] = True
            slay_list[i].append(0 - max_damage / 50 * anchor_y_idx)

        # Plotting tags of slay time for each character
        for char, slay_text, slay_time, slay_y_pos in slay_list:
            axes.plot([slay_time, slay_time], [target_hp, slay_y_pos], label=None, c=color_dict[char.name],
                      alpha=0.6, ls=ls_dict[char.rarity], lw=lw_dict[char.skill_order] / 2)
            if len(slay_text) <= 14:
                axes.text(slay_time - 0.4, slay_y_pos - max_damage / 320, slay_text, fontdict=SmallDescriptionFont,
                          bbox=dict(facecolor=color_dict[char.name], edgecolor=color_dict[char.name], alpha=0.4,
                                    pad=1.0),
                          horizontalalignment='right', verticalalignment='top')
            elif len(slay_text) <= 18:
                axes.text(slay_time - 0.4, slay_y_pos - max_damage / 320, slay_text, fontdict=TinyDescriptionFont,
                          bbox=dict(facecolor=color_dict[char.name], edgecolor=color_dict[char.name], alpha=0.4,
                                    pad=1.0),
                          horizontalalignment='right', verticalalignment='top')
            else:
                axes.text(slay_time - 0.4, slay_y_pos - max_damage / 320, slay_text, fontdict=ExtraTinyDescriptionFont,
                          bbox=dict(facecolor=color_dict[char.name], edgecolor=color_dict[char.name], alpha=0.4,
                                    pad=1.0),
                          horizontalalignment='right', verticalalignment='top')


def find_available_filename(stage, pick_list_name, multi_target_desc, enemy=None, defense=None, mr=None):
    """
    Find a valid filename to save figures
    """
    if not os.path.exists("figure/"):
        os.mkdir("figure/")
    if enemy:
        file_name = "figure/%s_%s_%s_%s" % (stage, enemy, pick_list_name, multi_target_desc)
        cnt = 0
        while os.path.exists(file_name + ".pdf") or os.path.exists(file_name + ".png"):
            cnt += 1
            file_name = "figure/%s_%s_%s_%s(%s)" % (stage, enemy, pick_list_name, multi_target_desc, cnt)
    else:
        file_name = "figure/%s_%s防_%s法抗_%s_%s" % (stage, defense, mr, pick_list_name, multi_target_desc)
     #   cnt = 0
     #   while os.path.exists(file_name + ".pdf") or os.path.exists(file_name + ".png"):
     #       cnt += 1
     #       file_name = "figure/%s_%s防_%s法抗_%s_%s(%s)" % (stage, defense, mr, pick_list_name, multi_target_desc, cnt)
    return file_name


def description_level_change(stage, char, desc):
    if stage[0] == "2":
        if char.rarity == 6:
            if int(desc[1:3]) > 90:
                desc = desc[0] + "90" + desc[3:]
        elif char.rarity == 5:
            if int(desc[1:3]) > 80:
                desc = desc[0] + "80" + desc[3:]
        elif char.rarity == 4:
            if int(desc[1:3]) > 70:
                desc = desc[0] + "70" + desc[3:]
    elif stage[0] == "1":
        if char.rarity == 6:
            if int(desc[1:3]) > 80:
                desc = desc[0] + "80" + desc[3:]
        elif char.rarity == 5:
            if int(desc[1:3]) > 70:
                desc = desc[0] + "70" + desc[3:]
        elif char.rarity == 4:
            if int(desc[1:3]) > 60:
                desc = desc[0] + "60" + desc[3:]
        elif char.rarity == 3:
            if int(desc[1:3]) > 55:
                desc = desc[0] + "55" + desc[3:]
    elif stage[0] == "1":
        if char.rarity == 6 or char.rarity == 5:
            if int(desc[1:3]) > 50:
                desc = desc[0] + "50" + desc[3:]
        elif char.rarity == 4:
            if int(desc[1:3]) > 45:
                desc = desc[0] + "45" + desc[3:]
        elif char.rarity == 3:
            if int(desc[1:3]) > 40:
                desc = desc[0] + "40" + desc[3:]
        elif char.rarity == 2 or char.rarity == 1:
            if int(desc[1:3]) > 30:
                desc = desc[0] + "30" + desc[3:]
    return desc


def set_damage_baseline(char_dict, stage, baseline, defense, mr, target_hp):
    """
    Set damage baseline.

    :return:    damage_baseline:    <int> damage baseline. This baseline is only used for calculating the percentage
                                        of each character's damage compared to damage baseline.
                                    E.g.    Specter-1(幽灵鲨-1技能) does 227,580 damage; while the baseline character,
                                              set as Matoimaru-1(缠丸-1技能), does 151,000 damage.
                                            Then `damage_baseline` is set as 151,000, and Specter does 184% damage.
                                              This percentage is shown in the legend to give an intuitive display of
                                              the damaging ability of each character.
    """
    if baseline:
        damage_baseline = char_dict[stage + "-" + baseline].simulate(defense, mr)[-1][1]
    elif target_hp:
        damage_baseline = target_hp
    else:
        damage_baseline = 100000
    return damage_baseline


def configure_mpl(axes, title, multi_target_lable=False):
    axes.set_title(title, fontdict=ExtraGiantFont)
    #axes.set_xlabel('时间', fontdict=GiantFont)
    #axes.set_ylabel('伤害总量', fontdict=GiantFont)
    #if multi_target_lable:
    #    axes.set_xlim([-10, 460])
    #else:
    #    axes.set_xlim([-10, 430])
    #axes.set_xticks([30 * k for k in range(11)])
    #axes.yaxis.set_major_locator(MultipleLocator(50000))
    #axes.grid(axis="both", ls=(10, (30, 5)), c="lightgray")
    axes.margins(0.05, 0.05)
    plt.subplots_adjust(top=0.95, bottom=0.08, right=0.98, left=0.1, hspace=0, wspace=0)


def plot(stage, pick_list, pick_list_name, baseline, enemy=None, defense=2000, mr=0,
         show_slay_line=True, multi_target=True, ignore_polish=True):
    """
    Plot damage curve.

    :param stage:           <str> A string indicating character stage.
                                {"29010", "25010", "2307", or "1507"} ("1507" is not recommended, may exist bugs)
    :param pick_list:       <str> A list of characters you want to show in the figure.
                                Element Format:
                                    "<CharName>" or "<CharName> <SkillOrder>"
                                Element Example:
                                    "陈": ensure all data of 3 skills of 陈 will be plotted
                                    "陈2": only plot the data of 陈 with her 2nd skill
    :param pick_list_name:  <str> the name of picklist, e.g. "56星近卫"
    :param baseline:        <str> A string indicating the baseline character.
                                If `BaselineChar` is assigned, the damage curve figure will show the damage curve of the
                                  character regardless of whether the character is in `PickList`. Her final damage will
                                  be regarded as the baseline damage (i.e. shown as 100%).
                                If not assigned, the baseline damage will be set equal to slay line (introduced below).
                                If neither of `Baseline` and `Enemy` are set, baseline damage will be set as 100,000.
                                Format:
                                    "<CharName> - <SkillOrder> 技能"
                                Example:
                                    "缠丸-1技能"
    :param enemy:           <str> A string indicating enemy target.
                                If `Enemy` is assigned, `Defense` and `MR` will refer to the data of the assigned
                                  target.
                                Available enemies in `character.enemy_dict`
                                Default: None
    :param defense:         <int> Defense value used in calculation.
                                It is effective only if `Enemy` is not assigned or assigned as empty string.
                                Default: 300
    :param mr:              <int> Magic resistance value used in calculation.
                                It is effective only if `Enemy` is not assigned or assigned as empty string.
                                Default: 30
    :param show_slay_line:  <bool> Whether to show slay line or not.
                                If True, the figure of damage curve will show an extra line to indicate the HP of enemy
                                  target and give an intuitive display of how much time a character takes to slay it.
                                It is effective only if `Enemy` is not assigned or assigned as empty string.
                                Default: True
    :param multi_target:    <bool> Whether to calculate damage in multi-target mode.
                                If True, the final result will be the damage expectation where characters can cause
                                  damage to multiple enemies.
                                For example, Specter(幽灵鲨) hits `2.6` targets per attack (on average), and the damage
                                  of Specter will be 2.6 times of the damage when not in multi-target mode.
                                You can arbitrarily change the value of how many targets one can hit per attack, like
                                  changing `2.6` to `2.5`, or even `3.0`, as you wish.
                                Default: True
    :param ignore_polish:   <bool> Whether to ignore the legend of characters with too low damage.
                                If True, then the figure will not show the legends for curves with damage less than
                                  `polish_line`. This often happens when the enemy is with extremely high defense or
                                  magic resistance, and each attack only causes less than 10% or even 5% of the damage
                                  when facing targets with 0 defense and MR.
                                By default, polish line is set as:
                                    polish_line = (max_damage / 10,000) ** (1 / 2) * 10,000
                                In most cases, characters with damage less than `polish_line` is with
                                  DPS < 220 (Single Target) / DPS < 320 (Multi Target).
                                Default: True

    :return: None
    """
    # Prepare
    f = csv.DictReader(open("raw/RawData.csv", 'r'))
    fig = plt.figure(num=1, figsize=(15, 8), dpi=240)
    ax = fig.add_subplot(1, 1, 1)
    if not os.path.exists("data/"):
        os.mkdir("data/")

    if enemy:
        target_num, target_hp, defense, mr = plot_enemy_info(fig, enemy)
        write_file = open("data/DamageRecord_%s_%s_%s.txt" % (stage, enemy, multitarget2str[multi_target]), "w")
        file_name = find_available_filename(stage, pick_list_name, multitarget2str[multi_target], enemy=enemy)
    else:
        target_num, target_hp = None, None
        show_slay_line = False
        write_file = open("data/DamageRecord_%s_%s_%s_%s.txt" % (stage, defense, mr, multitarget2str[multi_target]),
                          "w")
        file_name = find_available_filename(stage, pick_list_name, multitarget2str[multi_target], defense=defense,
                                            mr=mr)
    char_dict = modify_data(f, stage, multi_target)

    # Configure Matplotliba
    title = "%s，%s防御，%s法抗，300秒平均Dps，%s" % (stage, defense, mr, multitarget2str[multi_target])
    configure_mpl(ax, title, multi_target)

    # Set damage baseline
    # damage_baseline = set_damage_baseline(char_dict, stage, baseline, defense, mr, target_hp)

    # Plot curve
    legend_list, slay_list = plot_curve(char_dict, stage, write_file, ax, pick_list, defense, mr, baseline,
                                        show_slay_line, target_hp)

    # Plot legends
   # max_mamage = plot_legend(ax, legend_list, damage_baseline, ignore_polish, multi_target)

    # Plot slay line
   # if show_slay_line:
   #     plot_slay_line(ax, slay_list, target_num, enemy, target_hp, max_mamage)

    # Save result
   # plt.savefig(file_name + ".pdf")
    plt.savefig(file_name + ".png")
    # plt.show()
    plt.clf()


# Preset Parameters
DefaultPickList = {
    "Support": {
        "PickListName": "辅助",
        "PickList": ["地灵", "真理", "格劳克斯", "安洁莉娜", "初雪"],
        "Baseline": "初雪-1技能"
    },
    "Tank": {
        "PickListName": "重装",
        "PickList": ["雷蛇", "星熊", "坚雷", "火神", "年"],
        "Baseline": "火神-1技能"
    },
    "Special": {
        "PickListName": "特种",
        "PickList": ["阿消", "食铁兽", "暗索", "崖心", "雪雉", "伊桑", "狮蝎", "阿"],
        "Baseline": "食铁兽-1技能"
    },
    "Vanguard": {
        "PickListName": "先锋",
        "PickList": ["清道夫", "德克萨斯", "推进之王", "讯使", "凛冬", "桃金娘", "红豆", "格拉尼", "苇草"],
        "Baseline": "清道夫-1技能"
    },
    "SniperA": {
        "PickListName": "狙击A",
        "PickList": ["杰西卡", "流星", "流星(对空)", "红云", "白雪", "陨星", "安比尔", "守林人", "守林人(远程敌人)"],
        "Baseline": "杰西卡-1技能"
    },
    "SniperB": {
        "PickListName": "狙击B",
        "PickList": ["蓝毒", "白金", "灰喉", "能天使", "普罗旺斯", "普罗旺斯(正前方一格)", "黑", "送葬人", "送葬人(前方一排)"],
        "Baseline": "杰西卡-1技能"
    },
    "Caster": {
        "PickListName": "术师",
        "PickList": ["夜烟", "夜魔", "阿米娅", "艾雅法拉", "格雷伊", "远山", "天火", "莫斯提马", "伊芙利特"],
        "Baseline": "夜魔-2技能"
    },
    "GuardA": {
        "PickListName": "近卫A",
        "PickList": ["缠丸", "炎客", "芙兰卡", "杜宾", "诗怀雅", "慕斯", "霜叶", "艾丝黛尔", "暴行", "猎蜂"],
        "Baseline": "缠丸-1技能"
    },
    "GuardB": {
        "PickListName": "近卫B",
        "PickList": ["星极", "拉普兰德", "银灰", "幽灵鲨", "布洛卡", "煌", "赫拉格", "陈", "因陀罗"],
        "Baseline": "缠丸-1技能"
    },
    "MeleePhysical": {
        "PickListName": "近战物理",
        "PickList": ["煌", "赫拉格", "陈", "银灰3"],
        "Baseline": None,
        "IgnorePolish": False
    },
    "MeleeMagic": {
        "PickListName": "近战法术",
        "PickList": ["布洛卡2", "星极", "拉普兰德2", "陈2", "慕斯"],
        "Baseline": None,
        "IgnorePolish": False
    },
    "RangedPhysical": {
        "PickListName": "高台物理",
        "PickList": ["送葬人", "陨星", "黑2", "黑3", "能天使2", "能天使3", "蓝毒"],
        "Baseline": None,
        "IgnorePolish": False
    },
    "RangedMagic": {
        "PickListName": "高台法术",
        "PickList": ["安洁莉娜", "艾雅法拉", "伊芙利特"],
        "Baseline": None,
        "IgnorePolish": False
    },
    "Control": {
        "PickListName": "控制",
        "PickList": ["格劳克斯2", "狮蝎1", "伊桑2", "食铁兽", "莫斯提马2", "安洁莉娜2", "安洁莉娜3"],
        "Baseline": None,
        "IgnorePolish": False
    },
    "Arts": {
        "PickListName": "法伤",
        "PickList": 
            ["地灵", "真理", "格劳克斯", "安洁莉娜", "初雪",
             "雷蛇", "坚雷", "白雪", "因陀罗",
             "夜烟", "夜魔", "阿米娅", "艾雅法拉", "格雷伊", "远山", "天火", "莫斯提马", "伊芙利特",
             "布洛卡", "星极", "拉普兰德2", "陈2", "慕斯"
             ],
        "Baseline": None,
        "IgnorePolish": False
    }
}

if __name__ == "__main__":
    # Parameters
    # TODO: You can set your parameters below
    Stage = "29010"
    Pick = DefaultPickList["Arts"]
    Enemy = None # "伐木老手"
    # Enemy = "梅菲斯特"
    # Enemy = "重装五十夫长"

    PickList = Pick["PickList"]
    PickListName = Pick["PickListName"]
    Baseline = Pick["Baseline"]
    ShowSlayLine = Pick.get("ShowSlayLine", True)
    MultiTarget = False # Pick.get("MultiTarget", True)
    IgnorePolish = Pick.get("IgnorePolish", False)
    # End Params

    print(PickList, Enemy)
    plot(Stage, PickList, PickListName, Baseline, Enemy,
         show_slay_line=ShowSlayLine, multi_target=MultiTarget, ignore_polish=IgnorePolish)
