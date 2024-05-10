Auto spec example
=================

CVL Domain example
------------------

.. cvl:rule:: ruleExampleCVLDomain(bool isInFavor, address user)

   We can add free text anywhere.

   :title: Best rule!
   :param isInFavor: for or against
   :param user: the user using the thing

Auto spec
---------

.. autospec:: /../../code/voting/Voting_solution.spec
   :cvlobject: onlyLegalVotedChanges sumResultsEqualsTotalVotes voterDecides
