.. code-block:: cvl

   methods {
       function balanceOf(address) external returns (uint256) envfree;
   }

   rule testBalance(address user) {
       assert balanceOf(user) > 0;
   }
