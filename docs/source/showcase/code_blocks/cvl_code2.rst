.. code-block:: cvl
   :linenos:
   :lineno-start: 7
   :emphasize-lines: 10,17
   :caption: CVL2 code example

   methods
   {
       function DataWarehouse.getRegisteredSlot(
           bytes32 blockHash,
           address account,
           bytes32 slot
       ) external returns (uint256) => _getRegisteredSlot(blockHash, account, slot);
   }
   
   ghost mapping(address => uint256) _exchangeRateSlotValue;
   
   function _getRegisteredSlot(
       bytes32 blockHash,
       address account,
       bytes32 slot
   ) returns uint256 {
       return _exchangeRateSlotValue[account];
   }

