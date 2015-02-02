from django import forms
from django.forms import ModelForm, Form
from wsoptimize.models import SkillsData, ClassesData, CharacterData, DisplayData, BuffsAssaultAlliesData
import json

class CharacterForm(ModelForm):

	class Meta:
		model = CharacterData
		exclude = ('id', 'name', 'asp')

	def __init__(self, *args, **kwargs):
		self.cdata = kwargs.pop('cdata')
		super(CharacterForm, self).__init__(*args, **kwargs)
		self.fields['s'] = forms.ChoiceField(choices=self.cdata)

	def _validate(self):
		print "Validating Character Information"
		dictc = self.cdata[0]
		for i in dictc.keys():
			print i, self.cdata[0][i]
			try:
				if not float(self.cdata[0][i]) >= 0:
					return False
			except:
				return False
		print "Validated"
		return True
	
	def _save(self, cid, classtype, asp):
		print "Saving Character Information"
		try:
			instance = CharacterData()
			instance.id = cid
			instance.classtype = classtype
			instance.asp = asp
			instance.pwr = self.cdata[0]['pwr']
			instance.chc = self.cdata[0]['chc']
			instance.chs = self.cdata[0]['chs']
			instance.pts = self.cdata[0]['pts']
			instance.pwr_mod = self.cdata[0]['mpwr']
			instance.dmg_mod = self.cdata[0]['mdmg']
			instance.chc_mod = self.cdata[0]['mchc']
			instance.chs_mod = self.cdata[0]['mchs']
			instance.save()
			print "Successfully Saved"
		except:
			print "Error with saving"

class SkillForm(ModelForm):

	class Meta:
		model = SkillsData
		fields = ['weight', 'tier']

	def __init__(self, *args, **kwargs):
		self.skills = kwargs.pop('skills')

		super(SkillForm, self).__init__(*args, **kwargs)
		self.fields['s'] = forms.ChoiceField(choices=self.skills)

	def _validate(self):
		print 'Validaing Skill Relationships...'
		for row in self.skills:
			try:
				if float(row['w']) < 0 or float(row['w']) > 1:
					print 'weight problem'
					return False
				if int(row['t']) < 0 or int(row['t']) > 8:
					print 'tier problem'
					return False
			except ValueError:
				print 'value problem'
				return False

		print 'Validated'
		return True
		
	def _save(self, skill_id, weights, tiers, analyze):
		print "Saving Skill Relationships"
		# print instance.objects.id

		for i, w, t, a in zip(skill_id, weights, tiers, analyze):
			try:
				instance = SkillsData.objects.get(id=i)
				instance.weight = w
				instance.tier = t
				instance.analyze = a
				instance.save()
			
			except e:
				print "Failed"

class BuffsAssaultAlliesForm(ModelForm):

	class Meta:
		model = BuffsAssaultAlliesData

	def __init__(self, *args, **kwargs):
		self.buffs = kwargs.pop('buffs')

		super(BuffsAssaultAlliesForm, self).__init__(*args, **kwargs)
		self.fields['s'] = forms.ChoiceField(choices=self.buffs)

	def _validate(self):
		return True

		return True
		
	def _save(self, skill_id, buffs):
		print "Saving Buffs Data"
		# print instance.objects.id

		for i, b in zip(skill_id, buffs):
			try:
				instance = BuffsAssaultAlliesData.objects.get(id=i)
				instance.Name = b['n']
				instance.Target = b['t']
				instance.Effect = b['e']
				instance.Type = b['mt']
				instance.Uptime = b['u']
				instance.Modifier = b['m']
				instance.Analyze = b['a']
				instance.save()
			
			except e:
				print "Failed"

class ClassTypeForm(forms.Form):
	def __init__(self, *args, **kwargs):
		classes = kwargs.pop("class_types")
		default_class = kwargs.pop("default_class")
		super(ClassTypeForm, self).__init__(*args, **kwargs)
		
		self.fields['s'] = forms.ChoiceField(choices=classes)
		self.fields['s'].initial = default_class

class DisplayForm(ModelForm):
	class Meta:
		model = DisplayData

	def __init__(self, *args, **kwargs):
		super(DisplayForm, self).__init__(*args, **kwargs)
		try:
			self.rdata = kwargs.pop("data")
		except:
			self.rdata = self._load()
		self.fields['s'] = forms.ChoiceField(choices=self.rdata)

	def _save(self):
		print "Saving Display Data"
		# clear all data first:
		DisplayData.objects.all().delete()

		for i, row in enumerate(self.rdata):
			try:
				instance = DisplayData()
				instance.id = i+1
				instance.name = row['name']
				instance.ap_o = row['ap_o']
				instance.cc_o = row['cc_o']
				instance.dmg_o = row['dmg_o']
				instance.y = json.dumps(row['y'])
				instance.x1 = json.dumps(row['x1'])
				instance.x2 = json.dumps(row['x2'])
				instance.save()

			except:
				print "Failed to save display data"
				return False

		print "Successfully Saved"
		return True

	def _load(self):
		instance = DisplayData.objects.all()
		data = []
		for row in instance:
			datarow = {}
			datarow['name'] = row.name
			datarow['ap_o'] = row.ap_o
			datarow['cc_o'] = row.cc_o
			datarow['dmg_o'] = row.dmg_o
			datarow['y'] = json.loads(row.y)
			datarow['x1'] = json.loads(row.x1)
			datarow['x2'] = json.loads(row.x2)
			data += [datarow]
			
		return data
				
