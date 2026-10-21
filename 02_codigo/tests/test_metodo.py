import unittest
import numpy as np
from analizar import calibrate, exposure_mask
class MethodTests(unittest.TestCase):
 def test_tied_cutoff_is_proportional(self):
  p=np.array([10.,20.,30.,40.]); r=np.array([-1.,0.,0.,1.]);s,cut=calibrate(p,r,.35)
  np.testing.assert_allclose(s,[1,.5,.5,0]);self.assertAlmostEqual(np.dot(p,s),35);self.assertEqual(cut,0)
 def test_population_weights_not_cell_counts(self):
  s,_=calibrate([90,10],[-1,1],.5);np.testing.assert_allclose(s,[50/90,0])
 def test_all_tied(self):
  s,_=calibrate([5,90,5],[1,1,1],.37);np.testing.assert_allclose(s,[.37]*3)
 def test_edge_rates(self):
  np.testing.assert_array_equal(calibrate([10,20],[1,2],0)[0],[0,0]);np.testing.assert_array_equal(calibrate([10,20],[1,2],1)[0],[1,1])
 def test_mask_thresholds_and_missing(self):
  a=np.array([.09,.1,.11,np.nan],dtype='float32');np.testing.assert_array_equal(exposure_mask(a,np.isfinite(a),.1,'>='),[False,True,True,False])
  np.testing.assert_array_equal(exposure_mask(np.array([29,30,31],dtype='float32'),[True]*3,30,'>'),[False,False,True])
 def test_union_and_exact_categories(self):
  m=np.array([[1,1,0,0],[1,0,1,0],[0,1,1,0]],dtype='uint8');n=m.sum(axis=0);p=np.array([5,10,20,30]);self.assertEqual(p[n>0].sum(),sum(p[n==k].sum() for k in range(1,5)));self.assertEqual(p.sum(),sum(p[n==k].sum() for k in range(5)))
if __name__=='__main__':unittest.main()
