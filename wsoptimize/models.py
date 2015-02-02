from django.db import models

class SkillsData(models.Model):
    id = models.TextField(primary_key=True)  # This field type is a guess.
    wsclass = models.TextField(blank=True)  # This field type is a guess.
    wstype = models.TextField(blank=True)  # This field type is a guess.
    name = models.TextField(blank=True)  # This field type is a guess.
    slope = models.TextField(blank=True)  # This field type is a guess.
    constant = models.TextField(blank=True)  # This field type is a guess.
    slope_tier = models.TextField(blank=True)  # This field type is a guess.
    constant_tier = models.TextField(blank=True)  # This field type is a guess.
    nhits = models.TextField(blank=True)  # This field type is a guess.
    weight = models.TextField(blank=True)
    tier = models.TextField(blank=True)
    analyze = models.TextField(blank=True)

    class Meta:
        managed = True
        db_table = 'skills_data'

    def __unicode__(self):
        return self.name


class ClassesData(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    classtype = models.CharField(max_length=30)

    class Meta:
        managed = True
        db_table = 'classes_data'

    def __unicode__(self):
        return self.classtype

class CharacterData(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    classtype = models.CharField(max_length=30)
    pwr = models.CharField(max_length=30)
    chc = models.CharField(max_length=30)
    chs = models.CharField(max_length=30)
    pts = models.CharField(max_length=30)
    asp = models.CharField(max_length=30)
    dmg_mod = models.TextField(blank=True)
    chc_mod = models.TextField(blank=True)
    chs_mod = models.TextField(blank=True)
    pwr_mod = models.TextField(blank=True)

    class Meta:
        managed = True
        db_table = u'character_data'

    def __unicode__(self):
        return self.name

class DisplayData(models.Model):
        # return {'name': skill_name, 'ap_o': x_max, 'cc_o': x_max_cc, 'dmg_o': y_max, 
            # 'x1': a_unscaled_power, 'x2': a_critical_chance, 'y': a_effective_damage} 
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=30)
    ap_o = models.CharField(max_length=30)
    cc_o = models.CharField(max_length=30)
    dmg_o = models.CharField(max_length=30)
    x1 = models.TextField(blank=True)
    x2 = models.TextField(blank=True)
    y = models.TextField(blank=True)

    class Meta:
        managed = True
        db_table = u'display_data'

    def __unicode__(self):
        return self.name

class BuffsAssaultAlliesData(models.Model):
    id = models.TextField(primary_key=True)  # This field type is a guess.
    Name = models.TextField(blank=True)  # This field type is a guess.
    Target = models.TextField(blank=True)  # This field type is a guess.
    Effect = models.TextField(blank=True)  # This field type is a guess.
    Type = models.TextField(blank=True)  # This field type is a guess.
    Uptime = models.TextField(blank=True)  # This field type is a guess.
    Modifier = models.TextField(blank=True)  # This field type is a guess.
    Analyze = models.TextField(blank=True)  # This field type is a guess.
    
    class Meta:
        managed = True
        db_table = 'buffs_allies_assault_data'

    def __unicode__(self):
        return self.Name