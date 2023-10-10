from tdw_gym.tdw_gym import TDW
from tdw_gym.h_agent import H_agent
from copy import deepcopy
import logging
import os

class Action:
    ACTIONS = ["move_forward", "turn_left", "turn_right", "get_object", "put_in", "drop", "send_message"]
    INDEX = dict(zip(ACTIONS, range(len(ACTIONS))))

class ActionHandler:
    action_handler = None
    
    def __init__(self, screen_size=256, number_of_agents=1, output_dir="human_interface/log"):
        self.screen_size = screen_size
        self.env = TDW(screen_size=screen_size, number_of_agents=number_of_agents)
        self.state, self.info, self.env_api = self.env.reset(seed=2824,
                                               options={"scene": "5a", "layout": 0, "seed": 2824, "task": "food"},
                                               output_dir=output_dir)
        self.output_dir = output_dir
        logger = init_logs(output_dir)
        os.makedirs(os.path.join(self.output_dir, "Images"), exist_ok=True)
        self.agents = []
        for i in range(1, number_of_agents):
            agent = H_agent(i, logger, max_frames=3000, output_dir=output_dir)
            os.makedirs(os.path.join(self.output_dir, "Images", str(i)), exist_ok=True)
            if self.info['goal_description'] is not None:
                agent.reset(goal_objects = self.info['goal_description'],
                            output_dir = self.output_dir,
                            env_api = self.env_api[i],
                            agent_color = self.info['agent_colors'][i],
                            agent_id = i)
            else:
                agent.reset(output_dir = self.output_dir)
            
            self.agents.append(agent)
        self.env.get_obs()
        self.save_image()
        self.get_obs()
    
    '''
    Act with a given action. It will check whether the action is valid.
    '''
    def act(self, action):
        if action["type"] == Action.INDEX["get_object"]:
            if not self.holding_object("left"):
                action["arm"] = "left"
            elif not self.holding_object("right"):
                action["arm"] = "right"
            else:
                return "No arm is available."
            
            visible = False
            for vis_obj in self.obs["visible_objects"]:
                if vis_obj["id"] == action["object"]:
                    if vis_obj["type"] > 1:
                        return "Object is not getable."
                    visible = True
                    break
            if not visible:
                return "Object is not visible."
            
        elif action["type"] == Action.INDEX["drop"]:
            if not self.holding_object(action["arm"]):
                return "No object to drop"
        
        action_dict = {"0": action} # human action
        for i, agent in enumerate(self.agents):
            action_dict[str(i + 1)] = agent.act(self.state[str(i + 1)])
        
        self.state, self.reward, self.done, self.info = self.env.step(action_dict)
        if self.done:
            return "Done!"
        
        self.save_image()
        self.get_obs()
        # implicitly return None
    
    def save_image(self):
        img = self.env.controller.replicants[0].dynamic.get_pil_image('img')
        img.save("human_interface/log/first_person_img.png")
    
    '''
    Get required observations from environment. The result observation is json-serializable.
    '''
    def get_obs(self):
        env_obs = self.env.obs["0"]
        self.obs = {}
        self.obs["held_objects"] = env_obs["held_objects"]
        self.obs["oppo_held_objects"] = env_obs["oppo_held_objects"]
        self.obs["messages"] = env_obs["messages"]
        
        # remove additional "None" objects
        visible_objects = []
        for obj in env_obs["visible_objects"]:
            if obj["id"] is not None:
                # change numpy int32 to python int
                obj_c = deepcopy(obj)
                obj_c["seg_color"] = []
                for i in obj["seg_color"]:
                    obj_c["seg_color"].append(int(i))
                visible_objects.append(obj_c)
        self.obs["visible_objects"] = visible_objects
        
        # change ndarray to array
        seg_mask = []
        for i in range(self.screen_size):
            row = []
            for j in range(self.screen_size):
                col = []
                for k in range(3):
                    col.append(int(env_obs["seg_mask"][i, j, k]))
                row.append(col)
            seg_mask.append(row)
        self.obs["seg_mask"] = seg_mask
    
    def holding_object(self, arm):
        if arm == "left":
            return self.obs["held_objects"][0]["id"] is not None
        else:
            return self.obs["held_objects"][1]["id"] is not None

def init_action_handler(screen_size, number_of_agents=1):
    ActionHandler.action_handler = ActionHandler(screen_size, number_of_agents)

def get_action_handler():
    return ActionHandler.action_handler

def init_logs(output_dir, name = 'simple_example'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join(output_dir, "output.log"))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger