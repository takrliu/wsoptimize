# import gspread
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate
import csv

# FUNCTIONS
# https://forums.wildstar-online.com/forums/index.php?/topic/120472-carbine-please-provide-dr-equation-for-ap/?p=1253284
def effective_power(power):
	BASE = 3599
	if power < BASE:
		return power

	diff = power - BASE
	arange = np.arange(1, diff, 1)
	partials = np.power(0.9997211, arange)
	return np.sum(partials) + BASE + 1

def effective_damage(effective_power, s, c, crit_chance, crit_severity, st, ct, t, n, modifier=1):
	damage = n*(effective_power*s + c + t*(effective_power*st +ct))
	expected_average_damage = damage*(1 + crit_chance*(crit_severity-1))*modifier
	return expected_average_damage

# CLASSES
# storage class
class Skill:
	def __init__(self):
		self.skill ={}
		self.info = {}
	def add_skill(self, name, local_max, unscaled_power, effective_power, critical_chance, effective_dmg, t, w, n):
		self.skill[name] = {}
		self.skill[name]['max'] = local_max
		self.skill[name]['ed'] = effective_dmg
		self.skill[name]['tier'] = t
		self.skill[name]['weight'] = w
		self.skill[name]['nhit'] = n
		if not 'up' in self.info.keys():
			self.info['up'] = unscaled_power
			self.info['ep'] = effective_power
			self.info['cc'] = critical_chance
			self.info['length'] = len(critical_chance)
	def add_global_optimize(self):
		None

		# self.skill[name]['up'] = unscaled_power
		# self.skill[name]['ep'] = effective_power
		# self.skill[name]['cc'] = critical_chance
		# self.skill[name]['length'] = len(critical_chance)


# main optmization class
class Optimize:
	def __init__(self, power, critical_chance, critical_hit_severity, point_allocations):
		# character data
		self.p = power # support or assault power
		self.chr = critical_chance # in decimals
		self.chs = critical_hit_severity # in decimals
		self.pts = int(point_allocations) # determined from the rune slots in your gear
		#constants
		self.POWER_SCALE = 0.75 # rune slots with AP or SP is 75% of rune valuation
		self.SKILL_CHECK = 0
		self.CHR_SCALE = 65.0
		#data
		self.s = Skill()
	def add_buffs(self, dmod=1, pmod=1, chc_mod=0, chs_mod=0):
		self.p = (1+pmod)*self.p
		self.dmg_modifier = 1+dmod
		self.chr += chc_mod
		self.chs += chs_mod
		print self.p
		print self.dmg_modifier
		print self.chr
		print self.chs
	
	def add_skills(self, names, slopes, constants, slopes_tier, constants_tier, tier, weights, n_hits):
		#takes in a list of skills
		if len(names) != len(slopes) or len(slopes) != len(constants):
			print "Error: Skills lists do not match"
			self.skillcheck = 0
			return

		s = np.array(slopes)
		c = np.array(constants)
		st = np.array(slopes_tier)
		ct = np.array(constants_tier)
		tier = np.array(tier)
		nhits = np.array(n_hits)
		w = np.array(weights)
		self.skill_names = names
		self.skill_array = np.matrix((s, c, st, ct, tier, w, n_hits)).T
		self.skillcheck = 1

	def optimize_skill(self, skill):
		#determine skill index
		if type(skill) is str or type(skill) is unicode:
			try:
				skill_index = [i for i,n in enumerate(self.skill_names) if skill.lower() == n.lower()][0]
				# self.skill_names.index(skill)
			except ValueError:
				print skill + " does not exist"
				return
		else:
			skill = skill
			if skill <= self.skill_array.shape[0]:
				skill_index = skill-1
			else:
				print "Skill #" + str(skill) + " does not exist"
				return
		skill_name = self.skill_names[skill_index]
		# assumptions
		# 1) Full AP runes, therefore AP before runes is power - total point allocation 
		power = self.p - self.pts*self.POWER_SCALE
		# 2) Every single rune can slot AP, not true, but not off by too much especially with espers/stalkers
		
		# constants
		s = self.skill_array[skill_index, 0] # slope
		c = self.skill_array[skill_index, 1] # base damage
		st = self.skill_array[skill_index, 2]
		ct = self.skill_array[skill_index, 3]
		t = self.skill_array[skill_index, 4]
		w = self.skill_array[skill_index, 5]
		n = self.skill_array[skill_index, 6]
		m = self.dmg_modifier

		# potential available assault power with runes
		a_unscaled_power = [i*self.POWER_SCALE + power for i in xrange(1, self.pts, 1)]
		# potential effective power using the soft cap formula
		a_effective_power = [effective_power(i*self.POWER_SCALE + power) for i in xrange(1, self.pts, 1)]
		# potential points in critical hit ratings, where 65 pts = 1% increase
		a_critical_chance = [(i*1/self.CHR_SCALE/100 + self.chr) for i in xrange(1, self.pts, 1)][::-1] #reverse the list
		# effective damage: average expected damage taking into account chr, chs
		a_effective_damage = [effective_damage(ep, s, c, cc, self.chs, st, ct, t, n, modifier=m) 
			for ep, cc in zip(a_effective_power, a_critical_chance)]


		# determine the optimal point
		ymax_idx = np.argmax(a_effective_damage)
		y_max = a_effective_damage[ymax_idx]
		x_max = a_unscaled_power[ymax_idx]
		x_max_cc = a_critical_chance[ymax_idx]*100
		local_maximum = [y_max, x_max, x_max_cc]

		# store data
		self.s.add_skill(skill_name, 
				local_maximum,
				a_unscaled_power,
				a_effective_power,
				a_critical_chance,
				a_effective_damage,
				t,
				w,
				n)

		print self.skill_names[skill_index].upper() + ' T' + str(int(t))
		print '%0.2f\n%0.2f AP\n%0.2f%%' % (y_max, x_max, a_critical_chance[ymax_idx]*100)
		print 
		return {'name': skill_name, 'ap_o': x_max, 'cc_o': x_max_cc, 'dmg_o': y_max, 
			'x1': a_unscaled_power, 'x2': a_critical_chance, 'y': a_effective_damage} 

	def graph_skill(self, skill_name=0, savefile=0):
		skill_name = skill_name.lower()
		if skill_name not in self.s.skill.keys():
			print skill_name + " has not been optimized"
			print "Optimized skills: " +  ' '.join(self.s.skill.keys())
			return
		# extract stored data
		print self.s.skill[skill_name]['max']

		a_unscaled_power = self.s.info['up']
		a_critical_chance = self.s.info['cc']
		a_effective_power = self.s.info['ep']
		a_effective_damage = self.s.skill[skill_name]['ed']
		
		x_max = self.s.skill[skill_name]['max'][1]
		y_max = self.s.skill[skill_name]['max'][0]

		maximum_string = '%0.2f\n%0.2f AP\n%0.2f%%' % (y_max, x_max, self.s.skill[skill_name]['max'][2])

		self.graph(a_unscaled_power, a_effective_damage, x_max, y_max, maximum_string, savefile, skill_name)

	def graph_all(self):
		None

	def graph(self, x, y, xmax=0, ymax=0, string='', savefile=0, title=''):

		fig, ax1 = plt.subplots()
		fig.set_facecolor('white')
		fig.suptitle(title, fontsize=24, x=0.08)
		ax2 = ax1.twiny()
		# fig.text(0, 1.08, 'test', horizontalalignment='left',fontsize=20, transform=ax2.transAxes)

		for item in [fig, ax1, ax2]:
			item.patch.set_visible(False)
		ax1.spines["top"].set_visible(False)    
		ax1.spines["right"].set_visible(False)  
		ax1.get_xaxis().tick_bottom()  
		ax1.get_yaxis().tick_left()
		# plotting  
		# fitting
		xx = np.linspace(min(x), max(x),1000)
		f = interpolate.UnivariateSpline(x, y)
		# plt.plot(xx, f(xx), 'r-')

		ax1.plot(xx, f(xx), 'b,')
		ax1.plot(xmax, f(xmax), 'rh')

		ax1.set_xlim(min(x), max(x))
		ax2.set_xlim(np.min(self.s.info['cc']), np.max(self.s.info['cc']))
		# ax1.set_ylim(int(np.min(y)), int(np.max(y)))
		ax1.set_ylim([np.min(y), np.max(y)+5])
		# print np.min(y)
		# print np.max(y)
		
		# ax1.set_ylim(np.min(y), np.max(y))
		
		ax2.invert_xaxis()
		# labels
		ax1.set_xlabel('Power (AP/SP)', fontsize=14)
		ax1.set_ylabel("Expected Average Damage", fontsize=14)
		ax2.set_xlabel('Critical Chance', fontsize=14)
			
		if xmax:
			ax1.annotate(string, xy=(xmax, ymax), 
				xytext=(xmax, ymax-0.002*ymax),
			    # arrowprops=dict(facecolor='black', shrink=0.001),
				)

		if savefile:
			plt.savefig('pics/' + title + '.png')
		else:
			plt.show()

	def print_to_gsheet(self):
		None

	def optimize_all_skills(self, graph=0):
		print "Optimizing All Skills\n"
		rows = self.s.info['length']
		cols = len(self.s.skill.keys())
		sum_ed = np.zeros((1,rows))
		data_ed = np.matrix(np.ones((rows, cols)))
		# print sum_ed +  np.array([self.s.skill['shred']['ed']])
		for i, s in enumerate(self.s.skill.keys()):
			print s, 'T' + str(int(self.s.skill[s]['tier'])), self.s.skill[s]['weight'], self.s.skill[s]['nhit'], '\n'
			sum_ed +=  np.array(self.s.skill[s]['ed'])*self.s.skill[s]['weight']
			m = np.matrix(self.s.skill[s]['ed'])*self.s.skill[s]['weight']
			data_ed[:,i] = m.transpose()
			

		m = np.hstack((data_ed, sum_ed.transpose()))
		
		# determine the optimal point
		sum_ed = sum_ed.tolist()[0]
		ymax_idx = np.argmax(sum_ed)
		y_max = sum_ed[ymax_idx]
		x_max = self.s.info['up'][ymax_idx]
		x_max_cc = self.s.info['cc'][ymax_idx]*100
		global_maximum = [y_max, x_max, x_max_cc]

		# print self.skill_names[skill_index].upper() + ' Tier: ' + str(int(t))
		global_max_string = '%0.2f\n%0.2f AP\n%0.2f%%' % (y_max, x_max, x_max_cc)
		print global_max_string + '\n'


		if graph:
			self.graph(np.array(self.s.info['up']), m[:,-1], x_max, y_max, global_max_string, 1, 'Total')

		return {'name': 'Overall', 'ap_o': x_max, 'cc_o': x_max_cc, 'dmg_o': y_max, 
			'x1': self.s.info['up'], 'x2': self.s.info['cc'], 'y': sum_ed} 
def optimize_all(character_array, skills_array, buffs_list):
	#character array:
		# def __init__(self, power, critical_chance, critical_hit_severity, point_allocations):
	#skills array
		# def add_skills(self, names, slopes, constants, slopes_tier, constants_tier, tier, weights, n_hits)
	skill_n = []
	skill_s = []
	skill_c = []
	skill_st = []
	skill_ct = []
	skill_t = []
	skill_w = []
	skill_nhits = []
	for r in skills_array:
		skill_n += [r[0]]
		skill_s += [float(r[1])]
		skill_c += [float(r[2])]
		skill_st += [float(r[3])]
		skill_ct += [float(r[4])]
		skill_t += [float(r[5])]
		skill_w += [float(r[6])]
		skill_nhits += [float(r[7])]
	
	# print skill_n
	# print skill_s
	# print skill_c
	# print skill_st
	# print skill_ct
	# print skill_w
	# print skill_t
	# print character_array
	# return

	opt = Optimize(character_array[0], character_array[1], character_array[2], character_array[3])
	opt.add_buffs(dmod=buffs_list[0], pmod=buffs_list[1], chc_mod=buffs_list[2], chs_mod=buffs_list[3])
	opt.add_skills(skill_n, skill_s, skill_c, skill_st, skill_ct, skill_t, skill_w, skill_nhits)
	# optimal AP, Critical Chance (%), optimal damage, damage list, critical chance list, AP list
	data = []
	for i in skill_n:
		data += [opt.optimize_skill(i)]

	data += [opt.optimize_all_skills()]
	for row in data:
		print row['name']
	# awesomeness = 0
	return data


if __name__=="__main__":
	LOCAL = 1

	if LOCAL:
		with open('C:\Users\Roger\Desktop\WS\\tempdata.csv', 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			i = 0
			ch_data = []
			skill_n = []
			skill_s = []
			skill_c = []
			skill_st = []
			skill_ct = []
			tiers = []
			skill_w = []
			skill_nhits = []
			for row in reader:
				if i < 4:
					ch_data += [float(row[1])]
				else:
					skill_n += [row[0].lower()]
					skill_s += [float(row[1].replace('%', ''))/100]
					skill_c += [float(row[2])]
					skill_st += [float(row[3].replace('%', ''))/100]
					skill_ct += [float(row[4])]
					tiers += [float(row[5])]
					skill_w += [float(row[6].replace('%', ''))/100]
					skill_nhits += [float(row[7])]
				i += 1

	# character info
	opt = Optimize(ch_data[0], ch_data[1], ch_data[2], ch_data[3])
	# skill info
	opt.add_skills(skill_n, skill_s, skill_c, skill_st, skill_ct, tiers, skill_w, skill_nhits)

	opt.optimize_skill('shred')
	opt.optimize_skill('impale')
	opt.optimize_skill('punish')
	opt.optimize_skill('CK')
	opt.optimize_skill('AW')

# with open('C:\Users\Roger\Desktop\WS\output.csv', 'wb') as csvfile:
# 	writer = csv.writer(csvfile, delimiter = ',')
# 	for row in data:
# 		writer.writerow(row)


